from django import forms
from .models import PurchaseOrder, VendorBill, SalesOrder, CustomerInvoice, Payment
from core.models import Contact, AnalyticalAccount


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['date', 'contact', 'analytical_account', 'expected_delivery_date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact': forms.Select(attrs={'class': 'form-control'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class VendorBillForm(forms.ModelForm):
    class Meta:
        model = VendorBill
        fields = ['date', 'contact', 'analytical_account', 'bill_number', 'due_date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact': forms.Select(attrs={'class': 'form-control'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'bill_number': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['date', 'contact', 'analytical_account', 'expected_delivery_date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact': forms.Select(attrs={'class': 'form-control'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CustomerInvoiceForm(forms.ModelForm):
    class Meta:
        model = CustomerInvoice
        fields = ['date', 'contact', 'analytical_account', 'invoice_number', 'due_date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact': forms.Select(attrs={'class': 'form-control'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'amount', 'payment_method', 'customer_invoice', 'vendor_bill', 'reference', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'customer_invoice': forms.Select(attrs={'class': 'form-control'}),
            'vendor_bill': forms.Select(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_invoice'].queryset = CustomerInvoice.objects.filter(status='posted')
        self.fields['vendor_bill'].queryset = VendorBill.objects.filter(status='posted')
