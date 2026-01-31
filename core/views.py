from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from .models import User, Contact, Product, AnalyticalAccount, AutoAnalyticalModel
from .forms import LoginForm, SignupForm, CreateUserForm, ContactForm, ProductForm, AnalyticalAccountForm, AutoAnalyticalModelForm


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data['login_id']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(login_id=login_id)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid Login Id or Password')
            except User.DoesNotExist:
                messages.error(request, 'Invalid Login Id or Password')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.role = 'invoicing'  # Only invoicing users can sign up
                    user.username = user.login_id  # Use login_id as username
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    messages.success(request, 'Account created successfully! Please login.')
                    return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    else:
        form = SignupForm()
    
    return render(request, 'core/signup.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def create_user_view(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.username = user.login_id
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    messages.success(request, 'User created successfully!')
                    return redirect('user_list')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
    else:
        form = CreateUserForm()
    
    return render(request, 'core/create_user.html', {'form': form})


@login_required
def dashboard_view(request):
    context = {}
    
    if request.user.role == 'admin':
        from transactions.models import CustomerInvoice, VendorBill, PurchaseOrder, SalesOrder, Payment
        from budgets.models import Budget
        
        budgets = Budget.objects.filter(is_active=True)
        total_budgeted = sum(b.budgeted_amount for b in budgets)
        total_actual = sum(b.actual_amount for b in budgets)
        
        context.update({
            'total_invoices': CustomerInvoice.objects.count(),
            'total_bills': VendorBill.objects.count(),
            'total_orders': PurchaseOrder.objects.count() + SalesOrder.objects.count(),
            'total_payments': Payment.objects.count(),
            'active_budgets': budgets.count(),
            'total_budgeted': total_budgeted,
            'total_actual': total_actual,
            'recent_invoices': CustomerInvoice.objects.all().order_by('-date')[:10],
        })
    elif request.user.role == 'portal':
        # Portal user sees their own invoices/bills
        from transactions.models import CustomerInvoice, VendorBill, PurchaseOrder, SalesOrder
        from core.models import Contact
        
        try:
            contact = Contact.objects.get(email=request.user.email)
            context.update({
                'invoices': CustomerInvoice.objects.filter(contact=contact, status='posted').order_by('-date'),
                'bills': VendorBill.objects.filter(contact=contact, status='posted').order_by('-date'),
                'orders': list(PurchaseOrder.objects.filter(contact=contact)[:3]) + 
                         list(SalesOrder.objects.filter(contact=contact)[:3]),
            })
        except Contact.DoesNotExist:
            pass
    
    return render(request, 'core/dashboard.html', context)


@login_required
def user_list_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'core/user_list.html', {'users': users})


# Master Data Views
@login_required
def contact_list_view(request):
    contacts = Contact.objects.all()
    return render(request, 'core/contact_list.html', {'contacts': contacts})


@login_required
def contact_create_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.created_by = request.user
            contact.save()
            messages.success(request, 'Contact created successfully!')
            
            # Send email invitation if contact has email
            if contact.email:
                # TODO: Implement email sending
                pass
            
            return redirect('contact_list')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact_form.html', {'form': form, 'title': 'Create Contact'})


@login_required
@user_passes_test(is_admin)
def contact_edit_view(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact updated successfully!')
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)
    
    return render(request, 'core/contact_form.html', {'form': form, 'title': 'Edit Contact', 'contact': contact})


@login_required
@user_passes_test(is_admin)
def contact_archive_view(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.is_active = False
    contact.save()
    messages.success(request, 'Contact archived successfully!')
    return redirect('contact_list')


@login_required
def product_list_view(request):
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})


@login_required
def product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Create Product'})


@login_required
@user_passes_test(is_admin)
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
@user_passes_test(is_admin)
def product_archive_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save()
    messages.success(request, 'Product archived successfully!')
    return redirect('product_list')


@login_required
def analytical_account_list_view(request):
    accounts = AnalyticalAccount.objects.all()
    return render(request, 'core/analytical_account_list.html', {'accounts': accounts})


@login_required
def analytical_account_create_view(request):
    if request.method == 'POST':
        form = AnalyticalAccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.created_by = request.user
            account.save()
            messages.success(request, 'Analytical Account created successfully!')
            return redirect('analytical_account_list')
    else:
        form = AnalyticalAccountForm()
    
    return render(request, 'core/analytical_account_form.html', {'form': form, 'title': 'Create Analytical Account'})


@login_required
@user_passes_test(is_admin)
def analytical_account_edit_view(request, pk):
    account = get_object_or_404(AnalyticalAccount, pk=pk)
    
    if request.method == 'POST':
        form = AnalyticalAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Analytical Account updated successfully!')
            return redirect('analytical_account_list')
    else:
        form = AnalyticalAccountForm(instance=account)
    
    return render(request, 'core/analytical_account_form.html', {'form': form, 'title': 'Edit Analytical Account', 'account': account})


@login_required
@user_passes_test(is_admin)
def analytical_account_archive_view(request, pk):
    account = get_object_or_404(AnalyticalAccount, pk=pk)
    account.is_active = False
    account.save()
    messages.success(request, 'Analytical Account archived successfully!')
    return redirect('analytical_account_list')


@login_required
def auto_analytical_model_list_view(request):
    models = AutoAnalyticalModel.objects.all()
    return render(request, 'core/auto_analytical_model_list.html', {'models': models})


@login_required
def auto_analytical_model_create_view(request):
    if request.method == 'POST':
        form = AutoAnalyticalModelForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.created_by = request.user
            model.save()
            messages.success(request, 'Auto Analytical Model created successfully!')
            return redirect('auto_analytical_model_list')
    else:
        form = AutoAnalyticalModelForm()
    
    return render(request, 'core/auto_analytical_model_form.html', {'form': form, 'title': 'Create Auto Analytical Model'})


@login_required
@user_passes_test(is_admin)
def auto_analytical_model_edit_view(request, pk):
    model = get_object_or_404(AutoAnalyticalModel, pk=pk)
    
    if request.method == 'POST':
        form = AutoAnalyticalModelForm(request.POST, instance=model)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auto Analytical Model updated successfully!')
            return redirect('auto_analytical_model_list')
    else:
        form = AutoAnalyticalModelForm(instance=model)
    
    return render(request, 'core/auto_analytical_model_form.html', {'form': form, 'title': 'Edit Auto Analytical Model', 'model': model})


@login_required
@user_passes_test(is_admin)
def auto_analytical_model_archive_view(request, pk):
    model = get_object_or_404(AutoAnalyticalModel, pk=pk)
    model.is_active = False
    model.save()
    messages.success(request, 'Auto Analytical Model archived successfully!')
    return redirect('auto_analytical_model_list')
