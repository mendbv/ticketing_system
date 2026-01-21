from django.contrib import admin
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Создаем простую форму для админки
class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    # Используем нашу упрощенную форму
    add_form = MyUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    
    # Поля, которые будут видны при создании через "+"
    fields = ('email', 'first_name', 'last_name', 'password', 'is_staff', 'is_active')

    def save_model(self, request, obj, form, change):
        # Хешируем пароль перед сохранением
        if not change:
            obj.set_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)