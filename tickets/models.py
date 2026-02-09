import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('paid', _('Paid / Waiting for Docs')),
        ('pending', _('Pending Review')),
        ('processing', _('Processing')),
        ('ready', _('Ready')),
        ('rejected', _('Rejected')),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    ticket_number = models.CharField(max_length=10, unique=True, blank=True)
    
    service_name = models.CharField(_("Service"), max_length=255, default="Unknown Service")
    variant_name = models.CharField(_("Option"), max_length=255, blank=True, null=True)
    price_paid = models.DecimalField(_("Price Paid"), max_digits=10, decimal_places=2, default=0.00)

    user_note = models.TextField(_("Description"), blank=True)
    
    staff_internal_note = models.TextField(_("Staff Note"), blank=True)
    
    document_bundle = models.FileField(_("Client Documents"), upload_to='client_docs/', blank=True, null=True, help_text="Archive with documents (.zip, .pdf)")
    
    result_document = models.FileField(_("Result Document"), upload_to='results/', blank=True, null=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='paid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = str(uuid.uuid4())[:8].upper()
            
        if self.document_bundle and self.status == 'paid':
            self.status = 'pending'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.ticket_number} - {self.service_name}"