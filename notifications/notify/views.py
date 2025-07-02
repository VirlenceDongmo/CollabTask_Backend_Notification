from rest_framework import generics, permissions
from .serializers import NotificationSerializer
from .models import Notification
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from django.core.mail import send_mail
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone



class CreateNotification(APIView):
    def post(self, request):
        try:
            # Vérification du content-type
            if request.content_type != 'application/json':
                return Response(
                    {'error': 'Content-Type must be application/json'},
                    status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
                )

            # Décodage des données JSON
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return Response(
                    {'error': 'Invalid JSON data'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validation des champs requis
            required_fields = ['destinataire', 'destinateur', 'type', 'contenu']
            if not all(field in data for field in required_fields):
                return Response(
                    {'error': f'Missing required fields. Required: {required_fields}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Sauvegarde de la notification en base de données
            notification = Notification.objects.create(
                destinataire=data['destinataire'],
                destinateur=data['destinateur'],
                type=data['type'],
                contenu=data['contenu'],
                tache=data.get('tache'),
                date_envoi=timezone.now(),
                lu=False
            )

            # Récupérer l'email de l'utilisateur
            user_email = self._get_user_email(data['destinataire'])
            if not user_email:
                print(f"Aucun email trouvé pour l'utilisateur {data['destinataire']}")

            # Envoyer l'email si send_email est True
            email_sent = False
            if user_email and data.get('send_email', False):
                try:
                    email_sent = self._send_notification_email(user_email, data['contenu'])
                    print(f"Email envoyé à {user_email}")
                except Exception as email_error:
                    print(f"Erreur lors de l'envoi de l'email: {str(email_error)}")

            # Réponse avec la notification créée
            return Response(
                {
                    'status': 'success',
                    'notification': {
                        'id': notification.id,
                        'destinataire': notification.destinataire,
                        'destinateur': notification.destinateur,
                        'type': notification.type,
                        'contenu': notification.contenu,
                        'tache': notification.tache,
                        'date_envoi': notification.date_envoi,
                        'lu': notification.lu
                    },
                    'email': user_email
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_user_email(self, user_id):
        try:
            print(f"Tentative de récupération de l'email pour l'utilisateur {user_id}")
            response = requests.get(
                f'{settings.USER_SERVICE_URL}/api/user/{user_id}/',
                headers={'Authorization': self.request.headers.get('Authorization')}
            )
            print(f"Réponse du service utilisateur: {response.status_code} - {response.text}")
            if response.status_code == 200:
                email = response.json().get('email')
                print(f"Email trouvé: {email}")
                return email
            return None
        except requests.RequestException as e:
            print(f"Erreur de requête: {str(e)}")
            return None

    def _send_notification_email(self, email, message):
        """Méthode helper pour envoyer des emails"""
        try:
            send_mail(
                subject="Nouvelle notification",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return False




class NotificationListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # # Vérifier si l'utilisateur est un administrateur
        # if not hasattr(request.user, 'role') or request.user.role != 'ADMIN':
        #     raise PermissionDenied("Seuls les administrateurs peuvent accéder à cette ressource.")

        # Récupérer toutes les notifications
        notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
    


class NotificationDeleteView(APIView):
    # permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        # # Vérifier si l'utilisateur est un administrateur
        # if not hasattr(request.user, 'role') or request.user.role != 'ADMIN':
        #     raise PermissionDenied("Seuls les administrateurs peuvent supprimer des notifications.")

        try:
            # Récupérer la notification à supprimer
            notification = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            raise NotFound("Notification non trouvée.")

        notification.delete()
        return Response({"message": "Notification supprimée avec succès."}, status=status.HTTP_204_NO_CONTENT)
    



class MarkAsRead(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_update(self, serializer):
        serializer.instance.is_read = True
        serializer.save()