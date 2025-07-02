from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Champs à afficher dans la liste
    list_display = ('id', 'type', 'contenu', 'destinataire', 'destinateur', 'tache', 'date_envoi', 'lu')
    
    # Champs pour filtrer
    list_filter = ('type', 'lu', 'date_envoi')
    
    # Champs pour la recherche
    search_fields = ('contenu', 'destinataire', 'destinateur')
    
    # Champs en lecture seule
    readonly_fields = ('date_envoi',)
    
    # Nombre d'éléments par page
    list_per_page = 25
    
    # Activer la modification dans la liste pour le champ 'lu'
    list_editable = ('lu',)
    
    # Afficher un aperçu du contenu (tronqué si trop long)
    def contenu_preview(self, obj):
        return obj.contenu[:100] + ('...' if len(obj.contenu) > 100 else '')
    contenu_preview.short_description = 'Contenu (aperçu)'
    
    # Remplacer contenu par contenu_preview dans list_display
    list_display = ('id', 'type', 'contenu_preview', 'destinataire', 'destinateur', 'tache', 'date_envoi', 'lu')

    class Meta:
        model = Notification