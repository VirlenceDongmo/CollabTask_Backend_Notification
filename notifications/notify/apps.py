from django.apps import AppConfig
import threading
from django.conf import settings



class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notify'

    def ready(self):
        """Démarre le consumer RabbitMQ"""
        print("Django apps are ready, starting consumer...")
        
        # Démarrer le consumer dans tous les environnements
        from .consumers import start_consumer
        consumer_thread = threading.Thread(
            target=start_consumer,
            daemon=True,
            name="RabbitMQ_Consumer"
        )
        consumer_thread.start()
        print("Consumer thread started")



# class NotificationsConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'notify'  

#     def ready(self):
#         """Se lance une fois que Django est complètement chargé"""
#         print("Django apps are ready, starting consumer...")
#         if not settings.DEBUG:  
#             from .consumers import start_consumer
#             consumer_thread = threading.Thread(
#                 target=start_consumer,
#                 daemon=True
#             )
#             consumer_thread.start()