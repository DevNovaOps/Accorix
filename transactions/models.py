from django.db import models
from django.core.validators import MinValueValidator
from core.models import User, Contact, Product, AnalyticalAccount, AutoAnalyticalModel
from decimal import Decimal


class Transaction(models.Model):
    """Base model for all transactions"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    analytical_account = models.ForeignKey(AnalyticalAccount, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        abstract = True
        ordering = ['-date', '-created_at']


class PurchaseOrder(Transaction):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_purchase_orders')
    expected_delivery_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"PO-{self.transaction_number}"
    
    @property
    def total_amount(self):
        return sum(item.line_total for item in self.items.all())


class VendorBill(Transaction):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_vendor_bills')
    bill_number = models.CharField(max_length=50, blank=True)
    due_date = models.DateField()
    payment_status = models.CharField(max_length=20, default='not_paid', choices=[
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
    ])
    
    def __str__(self):
        return f"VB-{self.transaction_number}"
    
    @property
    def total_amount(self):
        return sum(item.line_total for item in self.items.all())
    
    @property
    def paid_amount(self):
        return sum(payment.amount for payment in self.payments.all())
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount
    
    def update_payment_status(self):
        paid = self.paid_amount
        total = self.total_amount
        
        if paid == 0:
            self.payment_status = 'not_paid'
        elif paid >= total:
            self.payment_status = 'paid'
        else:
            self.payment_status = 'partially_paid'
        self.save()


class SalesOrder(Transaction):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sales_orders')
    expected_delivery_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"SO-{self.transaction_number}"
    
    @property
    def total_amount(self):
        return sum(item.line_total for item in self.items.all())


class CustomerInvoice(Transaction):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customer_invoices')
    invoice_number = models.CharField(max_length=50, blank=True)
    due_date = models.DateField()
    payment_status = models.CharField(max_length=20, default='not_paid', choices=[
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
    ])
    
    def __str__(self):
        return f"INV-{self.transaction_number}"
    
    @property
    def total_amount(self):
        return sum(item.line_total for item in self.items.all())
    
    @property
    def paid_amount(self):
        return sum(payment.amount for payment in self.payments.all())
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount
    
    def update_payment_status(self):
        paid = self.paid_amount
        total = self.total_amount
        
        if paid == 0:
            self.payment_status = 'not_paid'
        elif paid >= total:
            self.payment_status = 'paid'
        else:
            self.payment_status = 'partially_paid'
        self.save()


class TransactionItem(models.Model):
    """Base model for transaction line items"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    analytical_account = models.ForeignKey(AnalyticalAccount, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    
    class Meta:
        abstract = True
    
    @property
    def line_total(self):
        return self.quantity * self.unit_price


class PurchaseOrderItem(TransactionItem):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    
    class Meta:
        ordering = ['id']


class VendorBillItem(TransactionItem):
    vendor_bill = models.ForeignKey(VendorBill, on_delete=models.CASCADE, related_name='items')
    
    class Meta:
        ordering = ['id']


class SalesOrderItem(TransactionItem):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    
    class Meta:
        ordering = ['id']


class CustomerInvoiceItem(TransactionItem):
    customer_invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name='items')
    
    class Meta:
        ordering = ['id']


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
    ]
    
    payment_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Link to invoice or bill
    customer_invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    vendor_bill = models.ForeignKey(VendorBill, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"PAY-{self.payment_number}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update payment status on related invoice/bill
        if self.customer_invoice:
            self.customer_invoice.update_payment_status()
        if self.vendor_bill:
            self.vendor_bill.update_payment_status()
