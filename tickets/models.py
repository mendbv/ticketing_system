import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('ready', _('Ready')),
        ('rejected', _('Rejected')),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    ticket_number = models.CharField(max_length=10, unique=True, blank=True)
    user_note = models.TextField(_("Client Note"))
    staff_internal_note = models.TextField(_("Staff Note"), blank=True)
    document = models.FileField(upload_to='documents/', blank=True, null=True)
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = str(uuid.uuid4())[:8].upper()
        
        if self.document and self.status == 'pending':
            self.status = 'ready'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.client}"