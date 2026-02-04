from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text="FontAwesome class (e.g., fa-solid fa-home)")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(Category, related_name='services', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    documents_required = models.TextField(help_text=_("List required documents here"))
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Base price"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (€{self.price})"

class ServiceVariant(models.Model):
    service = models.ForeignKey(Service, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text=_("e.g. ISEE Corrente"))
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} (+€{self.price})"