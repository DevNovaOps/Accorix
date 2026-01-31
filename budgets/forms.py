from django import forms
from .models import Budget
from core.models import AnalyticalAccount


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'analytical_account', 'start_date', 'end_date', 'budgeted_amount', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'budgeted_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
