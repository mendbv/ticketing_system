from django import forms
from .models import Ticket

# Форма для клиента (создание тикета)
class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['user_note', 'document']
        widgets = {
            'user_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your request...'}),
            # document уже будет файловым полем
        }

# Форма для сотрудника (редактирование тикета)
class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        # Сотрудник может менять статус, добавлять заметку, загружать готовый документ и ИНВОЙС
        fields = ['status', 'staff_internal_note', 'document', 'invoice']
        widgets = {
            'staff_internal_note': forms.Textarea(attrs={'rows': 3}),
        }