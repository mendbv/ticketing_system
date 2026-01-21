from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'client', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('ticket_number', 'client__email')