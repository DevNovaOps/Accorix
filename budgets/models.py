from django.db import models
from django.core.validators import MinValueValidator
from core.models import User, AnalyticalAccount
from decimal import Decimal


class Budget(models.Model):
    """Budget defined for a specific period and analytical account"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('archived', 'Archived'),
        ('cancelled', 'Cancelled'),
    ]
    
    STAGE_CHOICES = [
        ('planning', 'Planning'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('monitoring', 'Monitoring'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=255)
    analytical_account = models.ForeignKey(AnalyticalAccount, on_delete=models.CASCADE, related_name='budgets')
    start_date = models.DateField()
    end_date = models.DateField()
    budgeted_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='planning')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_budgets')
    
    class Meta:
        ordering = ['-start_date', 'analytical_account']
        unique_together = [['analytical_account', 'start_date', 'end_date']]
    
    def __str__(self):
        return f"{self.name} - {self.analytical_account} ({self.start_date} to {self.end_date})"
    
    @property
    def actual_amount(self):
        """Calculate actual amount from posted transactions"""
        from transactions.models import CustomerInvoice, VendorBill
        
        # Get all posted invoices and bills linked to this analytical account
        # within the budget period
        invoices = CustomerInvoice.objects.filter(
            analytical_account=self.analytical_account,
            status='posted',
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        bills = VendorBill.objects.filter(
            analytical_account=self.analytical_account,
            status='posted',
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        
        invoice_total = sum(inv.total_amount for inv in invoices)
        bill_total = sum(bill.total_amount for bill in bills)
        
        return invoice_total + bill_total
    
    @property
    def variance(self):
        """Difference between budgeted and actual"""
        return self.actual_amount - self.budgeted_amount
    
    @property
    def achievement_percentage(self):
        """Percentage of budget used"""
        if self.budgeted_amount == 0:
            return 0
        return (self.actual_amount / self.budgeted_amount) * 100
    
    @property
    def remaining_balance(self):
        """Remaining budget balance"""
        return self.budgeted_amount - self.actual_amount


class BudgetRevision(models.Model):
    """Track revisions/changes to budgets"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='revisions')
    previous_amount = models.DecimalField(max_digits=12, decimal_places=2)
    new_amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    revised_at = models.DateTimeField(auto_now_add=True)
    revised_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-revised_at']
    
    def __str__(self):
        return f"Revision of {self.budget} - {self.revised_at}"


class BudgetFieldExplanation(models.Model):
    """Field explanations for budget interface"""
    field_name = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    example = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.field_name} - {self.title}"


class BudgetStageMapping(models.Model):
    """Stage mapping configuration for budgets"""
    stage = models.CharField(max_length=50)
    description = models.TextField()
    color_code = models.CharField(max_length=7, default='#000000')  # Hex color
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.stage} - {self.description}"