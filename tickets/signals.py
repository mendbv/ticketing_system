from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Ticket

@receiver(post_save, sender=Ticket)
def notify_client_on_status_change(sender, instance, created, **kwargs):
    if not created and instance.status == 'ready':
        send_mail(
            'Your document is ready!',
            f'Hello! Your document for ticket {instance.ticket_number} is ready for download.',
            'from@company.it',
            [instance.client.email],
            fail_silently=False,
        )