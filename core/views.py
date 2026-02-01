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
    # Redirect portal users to their dashboard
    if request.user.is_portal_user:
        return redirect('portal_dashboard')
    
    context = {}
    
    if request.user.is_admin or request.user.role == 'invoicing':
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
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.created_by = request.user
            contact.save()
            
            # Automatically create portal user for customer/vendor contacts
            if contact.email and contact.contact_type in ['customer', 'vendor']:
                try:
                    # Check if user already exists
                    existing_user = User.objects.filter(email=contact.email).first()
                    if not existing_user:
                        # Create username from email
                        username = contact.email.split('@')[0]
                        login_id = username
                        
                        # Ensure unique login_id
                        counter = 1
                        while User.objects.filter(login_id=login_id).exists():
                            login_id = f"{username}{counter}"
                            counter += 1
                        
                        # Create the user
                        user = User.objects.create(
                            username=login_id,
                            login_id=login_id,
                            email=contact.email,
                            first_name=contact.name.split()[0] if contact.name else '',
                            last_name=' '.join(contact.name.split()[1:]) if len(contact.name.split()) > 1 else '',
                            role=contact.contact_type,
                            contact=contact,
                        )
                        
                        # Set a temporary password
                        temp_password = f"temp{contact.id}123"
                        user.set_password(temp_password)
                        user.save()
                        
                        messages.success(request, f'Contact and portal user created successfully! Login credentials - ID: {login_id}, Password: {temp_password}')
                        
                        # TODO: Send email invitation with login credentials
                        # send_portal_invitation_email(contact, login_id, temp_password)
                        
                    else:
                        # Link existing user to contact if not already linked
                        if not existing_user.contact:
                            existing_user.contact = contact
                            existing_user.role = contact.contact_type
                            existing_user.save()
                            messages.success(request, 'Contact created and linked to existing user!')
                        else:
                            messages.success(request, 'Contact created successfully!')
                            
                except Exception as e:
                    messages.warning(request, f'Contact created but failed to create portal user: {str(e)}')
            else:
                messages.success(request, 'Contact created successfully!')
            
            return redirect('contact_list')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact_form.html', {'form': form, 'title': 'Create Contact'})


@login_required
@user_passes_test(is_admin)
def contact_edit_view(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact updated successfully!')
            return redirect('contact_list')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ContactForm(instance=contact)
    
    return render(request, 'core/contact_form.html', {'form': form, 'title': 'Edit Contact', 'contact': contact})


@login_required
@user_passes_test(is_admin)
def contact_archive_view(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.is_active = False
    contact.status = 'archived'
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
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Create Product'})


@login_required
@user_passes_test(is_admin)
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
@user_passes_test(is_admin)
def product_archive_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.status = 'archived'
    product.save()
    messages.success(request, 'Product archived successfully!')
    return redirect('product_list')


@login_required
def analytical_account_list_view(request):
    accounts = AnalyticalAccount.objects.all()
    contacts = Contact.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    context = {
        'accounts': accounts,
        'contacts': contacts,
        'products': products,
    }
    
    return render(request, 'core/analytical_account_list.html', context)


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


@login_required
def analytics_master_view(request):
    analytical_accounts = AnalyticalAccount.objects.filter(is_active=True)
    contacts = Contact.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Handle auto analytical model creation
        model_name = request.POST.get('model_name')
        analytical_account_id = request.POST.get('analytical_account')
        partner_tag = request.POST.get('partner_tag')
        partner_id = request.POST.get('partner')
        product_category = request.POST.get('product_category')
        product_id = request.POST.get('product')
        
        if model_name and analytical_account_id:
            try:
                analytical_account = AnalyticalAccount.objects.get(id=analytical_account_id)
                
                # Create the auto analytical model
                auto_model = AutoAnalyticalModel.objects.create(
                    name=model_name,
                    analytical_account=analytical_account,
                    contact_type=partner_tag if partner_tag != 'Many to One ( From list )' else None,
                    product_category=product_category if product_category != 'Many to One ( From list )' else None,
                    created_by=request.user
                )
                
                messages.success(request, f'Auto Analytical Model "{model_name}" created successfully!')
                return redirect('analytics_master')
            except Exception as e:
                messages.error(request, f'Error creating model: {str(e)}')
    
    context = {
        'analytical_accounts': analytical_accounts,
        'contacts': contacts,
        'products': products,
    }
    
    return render(request, 'core/analytical_account_master.html', context)