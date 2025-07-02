import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

def sendMail(subject: str, receivers: list, template: str, context: dict):
    try:
        message = render_to_string(template, context)
        
        # ⚠️ Correction : `recipient_list` doit être en 3ème position
        send_mail(
            subject=subject,
            message=message,
            recipient_list=receivers,  # Liste/tuple attendu ici
            from_email=settings.EMAIL_HOST_USER,
            fail_silently=True,
            html_message=message
        )
        return True
    except Exception as e:
        logger.error(e)
        return False