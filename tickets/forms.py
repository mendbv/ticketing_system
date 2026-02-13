from django import forms
from .models import Ticket

class ClientUploadForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['document_bundle']
        widgets = {
            'document_bundle': forms.FileInput(attrs={'class': 'file-input'}),
        }

class StaffTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'staff_internal_note', 'result_document']
        widgets = {
            'staff_internal_note': forms.Textarea(attrs={'rows': 3}),
        }