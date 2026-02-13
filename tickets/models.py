import uuid
import os
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
    # Новое поле: Ответственный сотрудник
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets',
        verbose_name=_("Assignee")
    )
    
    ticket_number = models.CharField(max_length=10, unique=True, blank=True)
    service_name = models.CharField(_("Service"), max_length=255, default="Unknown Service")
    variant_name = models.CharField(_("Option"), max_length=255, blank=True, null=True)
    price_paid = models.DecimalField(_("Price Paid"), max_digits=10, decimal_places=2, default=0.00)
    
    user_note = models.TextField(_("Description"), blank=True)
    staff_internal_note = models.TextField(_("Staff Note"), blank=True)
    
    document_bundle = models.FileField(_("Legacy Bundle"), upload_to='client_docs/', blank=True, null=True)
    result_document = models.FileField(_("Result Document"), upload_to='results/', blank=True, null=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='paid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.ticket_number} - {self.service_name}"

class TicketFile(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='ticket_files/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

# НОВАЯ МОДЕЛЬ: Лог изменений
class TicketLog(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='logs', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255) # Например: "Changed status to Ready"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"