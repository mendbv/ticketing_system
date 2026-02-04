from django.contrib import admin
from .models import Category, Service, ServiceVariant

class ServiceVariantInline(admin.TabularInline):
    model = ServiceVariant
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceVariantInline]