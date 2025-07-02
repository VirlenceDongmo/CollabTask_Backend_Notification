from django.db import models
from django.utils import timezone

class Notification(models.Model):
    type = models.CharField(max_length=50)  # Type de notification ("Mise à jour", "Rappel", etc.)
    contenu = models.TextField()  
    destinataire = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID du collaborateur provenant du service externe"
    )
    destinateur = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID du collaborateur provenant du service externe"
    )
    tache = models.CharField(
        null=True,
        blank=True,
        help_text="ID de la tache provenant du service externe"
    )
    date_envoi = models.DateTimeField(default=timezone.now)  
    lu = models.BooleanField(default=False)  

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return f"Notification #{self.id} pour {self.destinataire}"




# from django.db import models
# from django.utils import timezone

# class Notification(models.Model):
#     user_id = models.PositiveIntegerField()
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(default=timezone.now)
#     related_object_id = models.PositiveIntegerField()
#     related_object_type = models.CharField(max_length=50)
#     email_sent = models.BooleanField(default=False)
#     email_sent_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Notification #{self.id} for user {self.user_id}"