from django.conf import settings
import requests
from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    destinataire_details = serializers.SerializerMethodField(read_only=True)
    destinateur_details = serializers.SerializerMethodField(read_only=True)
    tache_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'type', 'contenu', 'destinataire', 'destinateur', 'tache', 'date_envoi', 'lu', 'destinataire_details', 'destinateur_details', 'tache_details']
        extra_kwargs = {
            'destinataire': {'required': False, 'allow_null': True},
            'destinateur': {'required': False, 'allow_null': True},
            'tache': {'required': False, 'allow_null': True},
        }
        read_only_fields = ['id', 'created_at', 'destinateur']  # destinateur est en lecture seule

    def get_destinataire_details(self, obj):
        if not obj.destinataire:
            return {'nom': 'Non spécifié', 'email': None}
        try:
            request = self.context.get('request')
            headers = {'Content-Type': 'application/json'}
            if request and hasattr(request, 'headers') and 'Authorization' in request.headers:
                headers['Authorization'] = request.headers['Authorization']
            response = requests.get(
                f'{settings.USER_SERVICE_URL}/api/user/{obj.destinataire}/',
                headers=headers,
                timeout=2
            )
            response.raise_for_status()
            data = response.json()
            print(f"Destinataire details pour ID {obj.destinataire}: {data}")
            return data
        except Exception as e:
            print(f"Erreur récupération destinataire_details pour ID {obj.destinataire}: {str(e)}")
            return {'nom': 'Non spécifié', 'email': None}

    def get_destinateur_details(self, obj):
        if not obj.destinateur:
            return {'nom': 'Non spécifié', 'email': None}
        try:
            request = self.context.get('request')
            headers = {'Content-Type': 'application/json'}
            if request and hasattr(request, 'headers') and 'Authorization' in request.headers:
                headers['Authorization'] = request.headers['Authorization']
            response = requests.get(
                f'{settings.USER_SERVICE_URL}/api/user/{obj.destinateur}/',
                headers=headers,
                timeout=2
            )
            response.raise_for_status()
            data = response.json()
            print(f"Destinateur details pour ID {obj.destinateur}: {data}")
            return data
        except Exception as e:
            print(f"Erreur récupération destinateur_details pour ID {obj.destinateur}: {str(e)}")
            return {'nom': 'Non spécifié', 'email': None}

    def get_tache_details(self, obj):
        if not obj.tache:
            return {'titre': 'Aucune'}
        try:
            request = self.context.get('request')
            headers = {'Content-Type': 'application/json'}
            if request and hasattr(request, 'headers') and 'Authorization' in request.headers:
                headers['Authorization'] = request.headers['Authorization']
            response = requests.get(
                f'{settings.TASK_SERVICE_URL}/api/core/task/{obj.tache}/',
                headers=headers,
                timeout=2
            )
            response.raise_for_status()
            data = response.json()
            print(f"Tache details pour ID {obj.tache}: {data}")
            return data
        except Exception as e:
            print(f"Erreur récupération tache_details pour ID {obj.tache}: {str(e)} - Status code: {response.status_code if 'response' in locals() else 'N/A'}")
            return {'titre': 'Aucune'}