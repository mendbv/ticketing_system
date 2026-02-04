from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class SignUpForm(UserCreationForm):
    # ... (старый код SignUpForm остается без изменений) ...
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'})
    )
    first_name = forms.CharField(
        required=True, 
        label=_("First name"),
        widget=forms.TextInput(attrs={'placeholder': _('First Name')})
    )
    last_name = forms.CharField(
        required=True, 
        label=_("Last name"),
        widget=forms.TextInput(attrs={'placeholder': _('Last Name')})
    )
    phone = forms.CharField(
        required=False,
        label=_("Phone number"),
        widget=forms.TextInput(attrs={'placeholder': '+39 ... (Optional)'})
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user

# Новая форма для подтверждения профиля
class ProfileConfirmationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+39 ...'}),
        }