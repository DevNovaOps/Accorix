from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator
import re


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('portal', 'Portal User'),
        ('invoicing', 'Invoicing User'),
    ]
    
    login_id = models.CharField(
        max_length=12,
        unique=True,
        validators=[MinLengthValidator(6)],
        help_text="Login ID must be between 6-12 characters"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='invoicing')
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Contact(models.Model):
    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('both', 'Both'),
    ]
    
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    contact_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contacts')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AnalyticalAccount(models.Model):
    """Cost Centers - tracks where money is being spent"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_analytical_accounts')
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class AutoAnalyticalModel(models.Model):
    """Rules to automatically link transactions to analytical accounts"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    analytical_account = models.ForeignKey(AnalyticalAccount, on_delete=models.CASCADE)
    
    # Rule conditions
    product_category = models.CharField(max_length=100, blank=True, null=True)
    product_name_contains = models.CharField(max_length=255, blank=True, null=True)
    contact_type = models.CharField(max_length=10, blank=True, null=True)
    
    priority = models.IntegerField(default=0, help_text="Higher priority rules are evaluated first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_models')
    
    class Meta:
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name
