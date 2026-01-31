from django.db import models
from core.models import User


class PDFDocument(models.Model):
    """Model to store uploaded PDF documents"""
    DOCUMENT_TYPES = [
        ('invoice', 'Invoice'),
        ('bill', 'Bill'),
        ('receipt', 'Receipt'),
        ('statement', 'Statement'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    pdf_file = models.FileField(upload_to='documents/%Y/%m/')
    extracted_text = models.TextField(blank=True, help_text="Extracted text from PDF")
    extracted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    extracted_date = models.DateField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} ({self.document_type})"


class AnalyticsReport(models.Model):
    """Model to store generated analytics reports"""
    REPORT_TYPES = [
        ('revenue', 'Revenue Analysis'),
        ('expense', 'Expense Analysis'),
        ('profit_loss', 'Profit & Loss'),
        ('cash_flow', 'Cash Flow'),
        ('budget_variance', 'Budget Variance'),
        ('customer_analysis', 'Customer Analysis'),
        ('vendor_analysis', 'Vendor Analysis'),
    ]
    
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    chart_image = models.ImageField(upload_to='charts/%Y/%m/', null=True, blank=True)
    data_json = models.JSONField(default=dict, help_text="Chart data in JSON format")
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"