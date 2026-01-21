from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Employee(models.Model):
    ROLE_CHOICES = [
        ('manager', _('Manager')),
        ('consultant', _('Consultant')),
        ('lawyer', _('Lawyer')),
        ('support', _('Support')),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='consultant')
    photo = models.ImageField(upload_to='employees/', null=True, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return self.title

class ContactInfo(models.Model):
    whatsapp = models.CharField(max_length=50, blank=True)
    telegram = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Contact Settings"
        verbose_name_plural = "Contact Settings"

    def save(self, *args, **kwargs):
        if not self.pk and ContactInfo.objects.exists():
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return "Contact Details"