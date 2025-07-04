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
from rest_framework.exceptions import ValidationError

import logging



logger = logging.getLogger(__name__)

class CreateNotificationView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_create(self, serializer):
        # Vérifier que le destinateur, s'il est fourni, correspond à l'utilisateur connecté
        destinateur = self.request.data.get('destinateur')
        if destinateur and destinateur != str(self.request.user.id):
            logger.error(f"Validation error: destinateur {destinateur} does not match user {self.request.user.id}")
            raise ValidationError({"destinateur": "Le destinateur doit être l'utilisateur connecté ou null."})

        notification = serializer.save()
        logger.info(f"Notification créée: {notification.id}")

        # Vérifier si l'envoi d'email est requis
        send_email = self.request.data.get('send_email', False)
        if send_email and notification.destinataire:
            recipient_email = self._get_recipient_email(notification.destinataire)
            if recipient_email:
                self._send_email(notification, recipient_email)
            else:
                logger.warning(f"Aucun email valide trouvé pour le destinataire {notification.destinataire}")

    def _get_recipient_email(self, destinataire_id):
        """Récupérer l'email du destinataire via USER_SERVICE_URL."""
        try:
            response = requests.get(
                f'{settings.USER_SERVICE_URL}/api/user/{destinataire_id}/',
                headers={
                    'Authorization': self.request.headers.get('Authorization'),
                    'Content-Type': 'application/json',
                },
                timeout=2,
            )
            response.raise_for_status()
            user_data = response.json()
            email = user_data.get('email')
            logger.info(f"Email récupéré pour destinataire {destinataire_id}: {email}")
            return email
        except Exception as e:
            logger.error(f"Erreur récupération email destinataire {destinataire_id}: {str(e)}")
            return None

    def _send_email(self, notification, recipient_email):
        """Envoyer l'email directement avec send_mail."""
        try:
            send_mail(
                subject=f"Notification: {notification.type}",
                message=notification.contenu,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False
            )
            logger.info(f"Email envoyé à {recipient_email} pour la notification {notification.id}")
        except Exception as e:
            logger.error(f"Erreur envoi email à {recipient_email} pour la notification {notification.id}: {str(e)}")





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