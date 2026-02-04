from django.contrib import admin
from .models import Category, Service, ServiceVariant, Cart, CartItem

class ServiceVariantInline(admin.TabularInline):
    model = ServiceVariant
    extra = 1

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

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

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_price', 'updated_at')
    inlines = [CartItemInline]