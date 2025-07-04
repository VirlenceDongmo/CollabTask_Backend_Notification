from datetime import datetime
import logging
import time
import pika
import json
from django.core.mail import send_mail
from django.conf import settings
from django.apps import apps
from django.utils.dateparse import parse_datetime


def process_message(body):
    """Fonction de traitement des messages"""
    try:
        data = json.loads(body)


        # Nouvelle méthode de conversion de date compatible
        if 'due_date' in data and data['due_date']:
            try:
                # Solution pour toutes versions de Python
                dt = parse_datetime(data['due_date']) or datetime.strptime(data['due_date'], '%Y-%m-%d')
                data['due_date'] = dt.date() if dt else None
            except (ValueError, TypeError):
                data['due_date'] = None

        print(f" [x] Réception du message: {data}")
        
        Notification = apps.get_model('notify', 'Notification')
        
        # Traitement différencié selon le type d'événement
        if data['event_type'] == 'tâche créée':
            return _handle_task_creation(data, Notification)
        elif data['event_type'] == 'compte créé':
            return _handle_account_creation(data, Notification)
        elif data['event_type'] == 'tâche modifiée':
            return _handle_task_update(data, Notification)
        elif data['event_type'] == 'statut modifié':
            return _handle_status_change(data, Notification)
        elif data['event_type'] == 'tâche supprimée':
            return _handle_task_deletion(data, Notification)
        else:
            print(f"Type d'événement non reconnu: {data['event_type']}")
            return False
        
            
    except Exception as e:
        print(f"Erreur de traitement: {str(e)}")
        return False


def _handle_task_creation(data, Notification):
    """Gestion des créations de tâches"""
    try:
        # # Validation des données
        # required_fields = ['task_id', 'task_title', 'assigned_to', 'assigned_to_email']
        # if not all(k in data for k in required_fields):
        #     print(f"Données incomplètes pour la création de tâche: {data}")
        #     return False

        # Construire le contenu de la notification
        contenu = (
            f"Nouvelle tâche créée : {data['task_title']}\n"
            f"Description : {data.get('description', 'Non spécifiée')}\n"
            f"Échéance : {data.get('due_date', 'Non spécifiée')}"
        )

        # Création de la notification
        notification = Notification.objects.create(
            type='Tâche',
            contenu=contenu,
            destinataire=data['assigned_to'],
            destinateur=data.get('destinateur', None),
            tache=data['task_id'],
            lu=False
        )
        print(f"Notification créée: {notification.id}")

        # Envoi de l'email
        try:
            send_mail(
                subject=f"🆕 Tâche assignée : {data['task_title']}",
                message=f"""Bonjour,

Vous avez été assigné à une nouvelle tâche :
- Titre : {data['task_title']}
- Description : {data.get('description', 'Non spécifiée')}
- Date limite : {data.get('due_date', 'Non spécifiée')}

Veuillez vous connecter à {settings.PLATFORM_URL} pour plus de détails.

Cordialement,
L'équipe CollabTask""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[data['assigned_to_email']],
                fail_silently=False
            )
            print(f"Email envoyé à {data['assigned_to_email']}")
            return True
        except Exception as email_error:
            print(f"Échec de l'envoi de l'email: {str(email_error)}")
            return False

    except Exception as e:
        print(f"ERREUR dans _handle_task_creation: {str(e)}")
        return False   




logger = logging.getLogger(__name__)


def _handle_account_creation(data, Notification):
    try:
        print(f"Début traitement création compte: {data}")
        
        # # Validation des données
        # if not all(k in data for k in ['type', 'recipient', 'subject', 'contenu', 'destinataire', 'destinateur']):
        #     print("Données incomplètes pour la création de compte")
        #     return False

        # Création notification
        notification = Notification.objects.create(
            type=data['event_type'],
            contenu=data['contenu'],
            destinataire=data['destinataire'],
            destinateur = data['destinateur'],
        )
        print(f"Notification créée: {notification.id}")

        # Envoi email
        try:
            send_mail(
                subject=data['subject'],
                message=data['contenu'],
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[data['recipient']],
                fail_silently=False
            )
            print(f"Email envoyé à {data['recipient']}")
            return True
        except Exception as email_error:
            print(f"Échec envoi email: {str(email_error)}")
            return False
            
    except Exception as e:
        print(f"ERREUR dans _handle_account_creation: {str(e)}")
        return False

# def _handle_account_creation(data, Notification):
#     try:
#         print(f"Début traitement création compte: {data}")
        
#         # Validation des données
#         if not all(k in data for k in ['user_id', 'recipient', 'subject', 'body']):
#             print("Données incomplètes pour la création de compte")
#             return False

#         # Création notification
#         notification = Notification.objects.create(
#             user_id=data['user_id'],
#             message=f"Création de compte pour {data['recipient']}",
#             related_object_id=data['user_id'],
#             related_object_type='user',
#         )
#         print(f"Notification créée: {notification.id}")

#         # Envoi email
#         try:
#             send_mail(
#                 subject=data['subject'],
#                 message=data['body'],
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[data['recipient']],
#                 fail_silently=False
#             )
#             print(f"Email envoyé à {data['recipient']}")
#             return True
#         except Exception as email_error:
#             print(f"Échec envoi email: {str(email_error)}")
#             return False
            
#     except Exception as e:
#         print(f"ERREUR dans _handle_account_creation: {str(e)}")
#         return False


def _format_changes(changes):
    """Format changes for email notification."""
    formatted = []
    for key, value in changes.items():
        formatted.append(f"- {key.capitalize()}: {value if value is not None else 'Non spécifié'}")
    return "\n".join(formatted) if formatted else "Aucun changement spécifique."



def _handle_task_update(data, Notification):
    """Gestion des mises à jour de tâches"""
    try:
        # # Vérification des données obligatoires
        # required_fields = ['task_id', 'task_title', 'assigned_to', 'assigned_to_email']
        # if not all(k in data for k in required_fields):
        #     print(f"Données incomplètes pour la mise à jour de tâche: {data}")
        #     return False

        # Conversion de l'ID en entier si nécessaire
        destinataire_id = int(data['assigned_to']) if data['assigned_to'] else None

        # Construire le contenu de la notification
        contenu = (
            f"Tâche modifiée : {data['task_title']}\n"
            f"Changements :\n{_format_changes(data.get('changes', {}))}\n"
            f"Modifiée par : {data.get('initiator_name', 'Inconnu')}"
        )

        # Notification pour l'assigné
        if destinataire_id:
            Notification.objects.create(
                type='Tâche',
                contenu=contenu,
                destinataire=destinataire_id,
                destinateur=int(data['initiator_id']) if data.get('initiator_id') else None,
                tache=data['task_id'],
                lu=False
            )

        # Notification pour le créateur (si différent et si l'info existe)
        created_by = data.get('initiator_id')  # Utiliser initiator_id comme créateur
        if created_by and str(created_by) != str(data['assigned_to']):
            try:
                Notification.objects.create(
                    type='Tâche',
                    contenu=contenu,
                    destinataire=int(created_by),
                    destinateur=int(data['initiator_id']) if data.get('initiator_id') else None,
                    tache=data['task_id'],
                    lu=False
                )
            except (ValueError, TypeError) as e:
                print(f"Erreur création notification créateur: {e}")

        # Email à l'assigné
        if data.get('assigned_to_email'):
            try:
                send_mail(
                    subject=f"✏️ Tâche modifiée : {data['task_title']}",
                    message=f"""Bonjour,

La tâche "{data['task_title']}" a été modifiée par {data.get('initiator_name', 'un utilisateur')}.

Changements :
{_format_changes(data.get('changes', {}))}

Veuillez vous connecter à {settings.PLATFORM_URL} pour plus de détails.

Cordialement,
L'équipe CollabTask""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[data['assigned_to_email']],
                    fail_silently=False
                )
                print(f"Email envoyé à {data['assigned_to_email']}")
            except Exception as email_error:
                print(f"Échec de l'envoi de l'email: {str(email_error)}")
                return False

        return True

    except Exception as e:
        print(f"Erreur traitement mise à jour tâche: {str(e)}")
        return False
    


def _handle_status_change(data, Notification):
    """Gestion des changements de statut"""
    try:
        # # Vérification des données obligatoires
        # required_fields = ['task_id', 'task_title', 'assigned_to', 'assigned_to_email', 'old_status', 'new_status']
        # if not all(k in data for k in required_fields):
        #     print(f"Données incomplètes pour le changement de statut: {data}")
        #     return False

        # Conversion de l'ID en entier si nécessaire
        destinataire_id = int(data['assigned_to']) if data['assigned_to'] else None

        # Construire le contenu de la notification
        contenu = (
            f"Changement de statut de la tâche : {data['task_title']}\n"
            f"De : {data['old_status']}\n"
            f"À : {data['new_status']}\n"
            f"Initiateur : {data.get('initiator_name', 'Inconnu')}"
        )

        # Notification pour l'assigné
        if destinataire_id:
            Notification.objects.create(
                type='Statut',
                contenu=contenu,
                destinataire=destinataire_id,
                destinateur=int(data['initiator_id']) if data.get('initiator_id') else None,
                tache=data['task_id'],
                lu=False
            )

        # Notification pour les admins
        admin_recipients = []
        if isinstance(data.get('recipients'), str):
            admin_recipients = [{'email': data['recipients']}]
        elif isinstance(data.get('recipients'), list):
            admin_recipients = [{'email': email} for email in data['recipients']]

        for admin in admin_recipients:
            if isinstance(admin, dict) and admin.get('email'):
                try:
                    # Supposons que l'ID admin doit être récupéré via une API si nécessaire
                    Notification.objects.create(
                        type='Statut',
                        contenu=contenu,
                        destinataire=None,  # Admin ID non spécifié dans les données
                        destinateur=int(data['initiator_id']) if data.get('initiator_id') else None,
                        tache=data['task_id'],
                        lu=False
                    )
                except Exception as e:
                    print(f"Erreur création notification admin: {str(e)}")

        # Envoi des emails
        recipients = []
        if data.get('assigned_to_email'):
            recipients.append(data['assigned_to_email'])
        recipients.extend([admin.get('email') for admin in admin_recipients 
                          if isinstance(admin, dict) and admin.get('email')])

        if recipients:
            try:
                send_mail(
                    subject=f"⚠️ Changement de statut : {data['task_title']}",
                    message=f"""Bonjour,

Le statut de la tâche "{data['task_title']}" a changé :
- De : {data['old_status']}
- À : {data['new_status']}
- Initiateur : {data.get('initiator_name', 'Inconnu')}

Veuillez vous connecter à {settings.PLATFORM_URL} pour plus de détails.

Cordialement,
L'équipe CollabTask""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(set(recipients)),  # Évite les doublons
                    fail_silently=False
                )
                print(f"Email envoyé à {recipients}")
            except Exception as email_error:
                print(f"Échec de l'envoi de l'email: {str(email_error)}")
                return False

        return True

    except Exception as e:
        print(f"Erreur traitement changement statut: {str(e)}")
        return False


# def _handle_task_update(data, Notification):
#     """Gestion des mises à jour de tâches"""
#     try:
#         # Vérification des données obligatoires
#         if not data.get('assigned_to'):
#             print("Erreur: assigned_to manquant dans les données")
#             return False

#         # Conversion de l'ID en entier si nécessaire
#         user_id = int(data['assigned_to']) if data['assigned_to'] else None
        
#         # Notification pour l'assigné
#         if user_id:
#             Notification.objects.create(
#                 user_id=user_id,  # Utilisation de l'ID converti
#                 message=f"Mise à jour de la tâche: {data['task_title']}",
#                 related_object_id=data['task_id'],
#                 related_object_type='task',
#             )
        
#         # Notification pour le créateur (si différent et si l'info existe)
#         created_by = data.get('created_by')
#         if created_by and str(created_by) != str(data['assigned_to']):
#             try:
#                 Notification.objects.create(
#                     user_id=int(created_by),
#                     message=f"Mise à jour de votre tâche: {data['task_title']}",
#                     related_object_id=data['task_id'],
#                     related_object_type='task'
#                 )
#             except (ValueError, TypeError) as e:
#                 print(f"Erreur création notification créateur: {e}")

#         # Email à l'assigné
#         if data.get('assigned_to_email'):
#             send_mail(
#                 subject=f"✏️ Tâche modifiée: {data['task_title']}",
#                 message=f"""Bonjour,
                
# La tâche "{data['task_title']}" a été modifiée par {data.get('initiator_name', 'un utilisateur')}.

# Changements:
# {_format_changes(data.get('changes', {}))}

# Cordialement,
# L'équipe CollabTask""",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[data['assigned_to_email']],
#                 fail_silently=False
#             )
#         return True
        
#     except Exception as e:
#         print(f"Erreur traitement mise à jour tâche: {str(e)}")
#         return False
    


# def _handle_status_change(data, Notification):
#     """Gestion des changements de statut"""
#     try:
#         # Convertir admin_recipients en liste standardisée
#         admin_recipients = []
        
#         # Cas 1: Chaîne d'email unique
#         if isinstance(data.get('admin_recipients'), str):
#             admin_recipients = [{'email': data['admin_recipients']}]
#         # Cas 2: Liste de dictionnaires
#         elif isinstance(data.get('admin_recipients'), list):
#             admin_recipients = data['admin_recipients']
        
#         # Notification pour l'assigné
#         if data.get('assigned_to'):
#             Notification.objects.create(
#                 user_id=int(data['assigned_to']),
#                 message=f"Changement de statut: {data['task_title']} ({data['old_status']} → {data['new_status']})",
#                 related_object_id=data['task_id'],
#                 related_object_type='task',
#             )
        
#         # Notification pour les admins
#         for admin in admin_recipients:
#             if isinstance(admin, dict) and admin.get('email'):
#                 # Vous devrez peut-être récupérer l'ID admin via une API
#                 # Ici on suppose que admin est un dict avec 'id' et 'email'
#                 try:
#                     Notification.objects.create(
#                         user_id=int(admin.get('id', 0)),  # 0 ou une valeur par défaut
#                         message=f"Changement statut tâche: {data['task_title']}",
#                         related_object_id=data['task_id'],
#                         related_object_type='task',
    
#                     )
#                 except Exception as e:
#                     print(f"Erreur création notification admin: {str(e)}")

#         # Envoi des emails
#         recipients = []
#         if data.get('assigned_to_email'):
#             recipients.append(data['assigned_to_email'])
        
#         recipients.extend([admin.get('email') for admin in admin_recipients 
#                          if isinstance(admin, dict) and admin.get('email')])
        
#         if recipients:
#             send_mail(
#                 subject=f"⚠️ Changement de statut: {data['task_title']}",
#                 message=f"""Alerte,
                
# Le statut de la tâche "{data['task_title']}" a changé:
# De: {data['old_status']}
# À: {data['new_status']}

# Initiateur: {data.get('initiator_name', 'Inconnu')}

# Cordialement,
# L'équipe CollabTask""",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=list(set(recipients)),  # Évite les doublons
#                 fail_silently=False
#             )
#         return True
        
#     except Exception as e:
#         print(f"Erreur traitement changement statut: {str(e)}")
#         return False




def _handle_task_deletion(data, Notification):
    """Gestion des suppressions de tâches"""
    try:
        if data.get('assigned_to'):
            Notification.objects.create(
                user_id=data['assigned_to'],
                message=f"Tâche supprimée: {data['task_title']}",
                related_object_id=data['task_id'],
                related_object_type='task',
            )

        if data.get('assigned_to_email'):
            send_mail(
                subject=f"🗑️ Tâche supprimée: {data['task_title']}",
                message=f"""Bonjour,
                
La tâche "{data['task_title']}" a été supprimée par {data.get('deleted_by_name', 'un administrateur')}.

Cordialement,
L'équipe CollabTask""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[data['assigned_to_email']],
                fail_silently=False
            )
        return True
    except Exception as e:
        print(f"Erreur traitement suppression: {str(e)}")
        return False



def _format_changes(changes):
    """Formate les changements pour l'email"""
    formatted = []
    for field, value in changes.items():
        if field == 'due_date' and value:
            try:
                # Si c'est déjà une chaîne formatée, on l'utilise directement
                if isinstance(value, str):
                    # Essaye de parser la date si elle est au format ISO
                    if '-' in value and ':' in value:  # Format ISO probable
                        from datetime import datetime
                        date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                        value = date_obj.strftime('%d/%m/%Y')
                    else:
                        value = value  # Garde la valeur originale
                else:
                    # Si c'est un objet date, on le formate
                    value = value.strftime('%d/%m/%Y')
            except Exception as e:
                print(f"Erreur formatage date: {str(e)}")
                value = str(value)  # Fallback: conversion simple en string
        
        formatted.append(f"- {field}: {value or 'Non spécifié'}")
    
    return '\n'.join(formatted) if formatted else 'Aucun détail de modification'





def start_consumer():
    print("\n=== Initialisation du Consumer RabbitMQ ===")
    print(f"Configuration utilisée: Host={settings.RABBITMQ['HOST']}, Port={settings.RABBITMQ['PORT']}")

    while True:
        connection = None
        try:
            # Paramètres de connexion avec timeout ajustés
            params = pika.ConnectionParameters(
                host=settings.RABBITMQ['HOST'],
                port=settings.RABBITMQ['PORT'],
                credentials=pika.PlainCredentials(
                    settings.RABBITMQ['USER'],
                    settings.RABBITMQ['PASSWORD']
                ),
                virtual_host='/',
                heartbeat=600,  # Augmentez le heartbeat
                blocked_connection_timeout=300,
                connection_attempts=3,
                retry_delay=5
            )
            
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            # Déclaration des éléments RabbitMQ
            channel.exchange_declare(
                exchange=settings.RABBITMQ['EXCHANGE'],
                exchange_type='direct',
                durable=True
            )
            
            channel.queue_declare(
                queue=settings.RABBITMQ['QUEUE'],
                durable=True
            )
            
            for routing_key in settings.RABBITMQ['ROUTING_KEYS']:
                channel.queue_bind(
                    exchange=settings.RABBITMQ['EXCHANGE'],
                    queue=settings.RABBITMQ['QUEUE'],
                    routing_key=routing_key
                )

            # Callback et consommation
            def callback(ch, method, properties, body):
                try:
                    print(f"Message reçu: {body.decode()}")
                    success = process_message(body)  # <-- Ajoutez cette ligne
                    if success:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        print("Échec du traitement - message rejeté")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                except Exception as e:
                    print(f"Erreur traitement message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_consume(
                queue=settings.RABBITMQ['QUEUE'],
                on_message_callback=callback,
                auto_ack=False
            )

            print("Consumer prêt - En attente de messages...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Erreur connexion: {e} - Reconnexion dans 10s...")
            time.sleep(10)
        except pika.exceptions.AMQPChannelError as e:
            print(f"Erreur canal: {e} - Nouvelle connexion...")
            if connection and not connection.is_closed:
                connection.close()
            time.sleep(5)
        except Exception as e:
            print(f"Erreur inattendue: {e} - Reconnexion dans 15s...")
            if connection and not connection.is_closed:
                connection.close()
            time.sleep(15)