from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator
import re


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin (Business Owner)'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
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
    
    # Link to contact for portal users
    contact = models.OneToOneField('Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='user_account')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_portal_user(self):
        return self.role in ['customer', 'vendor']
    
    @property
    def is_admin(self):
        return self.role == 'admin'


class Contact(models.Model):
    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('both', 'Both'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    contact_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    image = models.ImageField(upload_to='contacts/', blank=True, null=True)
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contacts')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def tag_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags(self, tag_list):
        """Set tags from a list"""
        self.tags = ', '.join(tag_list) if tag_list else ''


class Product(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def tag_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags(self, tag_list):
        """Set tags from a list"""
        self.tags = ', '.join(tag_list) if tag_list else ''


class AnalyticalAccount(models.Model):
    """Cost Centers - tracks where money is being spent"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('archived', 'Archived'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
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
    STATUS_CHOICES = [
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    analytical_account = models.ForeignKey(AnalyticalAccount, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
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
