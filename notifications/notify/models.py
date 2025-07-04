from django.db import models
from django.utils import timezone

class Notification(models.Model):
    type = models.CharField(max_length=50)  
    contenu = models.TextField()  
    destinataire = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID du collaborateur provenant du service de gestion des collaborateurs"
    )
    destinateur = models.EmailField(max_length=254, default='collabtask86@gmail.com')
    tache = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID de la tache provenant du service de gestion des taches"
    )
    date_envoi = models.DateTimeField(default=timezone.now)  
    lu = models.BooleanField(default=False)  

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return f"Notification #{self.id} pour {self.destinataire}"

