from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Contact, Product, AnalyticalAccount, AutoAnalyticalModel


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'login_id', 'email', 'role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('login_id', 'role')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('login_id', 'role', 'email')}),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'contact_type', 'is_active', 'created_at']
    list_filter = ['contact_type', 'is_active']
    search_fields = ['name', 'email']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'unit_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku']


@admin.register(AnalyticalAccount)
class AnalyticalAccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(AutoAnalyticalModel)
class AutoAnalyticalModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'analytical_account', 'priority', 'is_active']
    list_filter = ['is_active', 'analytical_account']
    search_fields = ['name']
