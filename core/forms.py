from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
import re
from .models import User, Contact, Product, AnalyticalAccount, AutoAnalyticalModel


def validate_login_id(value):
    if len(value) < 6 or len(value) > 12:
        raise ValidationError('Login ID must be between 6-12 characters.')
    if User.objects.filter(login_id=value).exists():
        raise ValidationError('Login ID already exists.')


def validate_password_strength(value):
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[a-z]', value):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('Password must contain at least one special character.')


def validate_email_unique(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError('Email already exists in database.')


class LoginForm(forms.Form):
    login_id = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Login ID'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Password'
        })
    )


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Password',
            'id': 'id_password'
        }),
        validators=[validate_password_strength]
    )
    re_enter_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Re-Enter Password',
            'id': 'id_re_enter_password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'login_id', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'auth-input',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Last Name'
            }),
            'login_id': forms.TextInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Login ID'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Email ID'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login_id'].validators.append(validate_login_id)
        self.fields['email'].validators.append(validate_email_unique)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        re_enter_password = cleaned_data.get('re_enter_password')
        
        if password and re_enter_password and password != re_enter_password:
            raise ValidationError('Passwords do not match.')
        
        return cleaned_data


class CreateUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        validators=[validate_password_strength]
    )
    re_enter_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-Enter Password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'login_id', 'email', 'role', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'login_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Login ID'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email ID'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[('admin', 'Admin'), ('portal', 'Portal')]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login_id'].validators.append(validate_login_id)
        self.fields['email'].validators.append(validate_email_unique)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        re_enter_password = cleaned_data.get('re_enter_password')
        
        if password and re_enter_password and password != re_enter_password:
            raise ValidationError('Passwords do not match.')
        
        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'address', 'contact_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_type': forms.Select(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'category', 'unit_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class AnalyticalAccountForm(forms.ModelForm):
    class Meta:
        model = AnalyticalAccount
        fields = ['code', 'name', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AutoAnalyticalModelForm(forms.ModelForm):
    class Meta:
        model = AutoAnalyticalModel
        fields = ['name', 'description', 'analytical_account', 'product_category', 'product_name_contains', 'contact_type', 'priority', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'analytical_account': forms.Select(attrs={'class': 'form-control'}),
            'product_category': forms.TextInput(attrs={'class': 'form-control'}),
            'product_name_contains': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_type': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Any'), ('customer', 'Customer'), ('vendor', 'Vendor'), ('both', 'Both')]),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
