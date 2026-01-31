from django.db import models
from core.models import User
from transactions.models import CustomerInvoice, VendorBill


class StripePayment(models.Model):
    """Model to track Stripe payments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded'),
    ]
    
    # Stripe identifiers
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Related objects
    customer_invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, null=True, blank=True, related_name='stripe_payments')
    vendor_bill = models.ForeignKey(VendorBill, on_delete=models.CASCADE, null=True, blank=True, related_name='stripe_payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stripe_payments')
    
    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.stripe_payment_intent_id} - ₹{self.amount}"


class PaymentWebhook(models.Model):
    """Model to track Stripe webhook events"""
    stripe_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Webhook {self.stripe_event_id} - {self.event_type}"