from django import forms
from django.forms import inlineformset_factory
from .models import (
    PurchaseOrder, PurchaseOrderItem, VendorBill, VendorBillItem,
    SalesOrder, SalesOrderItem, CustomerInvoice, CustomerInvoiceItem,
    Payment, ChartOfAccounts
)
from core.models import Contact, Product, AnalyticalAccount


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(contact_type__in=['vendor', 'both'])


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity', 'unit_price', 'analytical_account', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(contact_type__in=['vendor', 'both'])


class VendorBillItemForm(forms.ModelForm):
    class Meta:
        model = VendorBillItem
        fields = ['product', 'quantity', 'unit_price', 'analytical_account', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(contact_type__in=['customer', 'both'])


class SalesOrderItemForm(forms.ModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ['product', 'quantity', 'unit_price', 'analytical_account', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(contact_type__in=['customer', 'both'])


class CustomerInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = CustomerInvoiceItem
        fields = ['product', 'quantity', 'unit_price', 'analytical_account', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'amount', 'payment_method', 'reference', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ChartOfAccountsForm(forms.ModelForm):
    class Meta:
        model = ChartOfAccounts
        fields = ['account_code', 'account_name', 'account_type', 'parent_account', 'status']
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'parent_account': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# Budget Override Form
class BudgetOverrideForm(forms.Form):
    override_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Reason for Budget Override',
        help_text='Please provide a detailed reason for exceeding the budget limit.'
    )
    confirm_override = forms.BooleanField(
        label='I confirm that I want to proceed despite exceeding the budget',
        required=True
    )


# Formsets for inline editing
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemForm,
    extra=1, can_delete=True, min_num=1, validate_min=True
)

VendorBillItemFormSet = inlineformset_factory(
    VendorBill, VendorBillItem, form=VendorBillItemForm,
    extra=1, can_delete=True, min_num=1, validate_min=True
)

SalesOrderItemFormSet = inlineformset_factory(
    SalesOrder, SalesOrderItem, form=SalesOrderItemForm,
    extra=1, can_delete=True, min_num=1, validate_min=True
)

CustomerInvoiceItemFormSet = inlineformset_factory(
    CustomerInvoice, CustomerInvoiceItem, form=CustomerInvoiceItemForm,
    extra=1, can_delete=True, min_num=1, validate_min=True
)