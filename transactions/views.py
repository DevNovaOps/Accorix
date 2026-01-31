from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import date
from .models import (
    PurchaseOrder, VendorBill, SalesOrder, CustomerInvoice, Payment,
    PurchaseOrderItem, VendorBillItem, SalesOrderItem, CustomerInvoiceItem
)
from core.models import Contact, Product, AnalyticalAccount, AutoAnalyticalModel
from .forms import (
    PurchaseOrderForm, VendorBillForm, SalesOrderForm, CustomerInvoiceForm, PaymentForm
)


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def apply_auto_analytical_model(transaction_item, contact, product):
    """Apply auto analytical models to determine analytical account"""
    models = AutoAnalyticalModel.objects.filter(is_active=True).order_by('-priority')
    
    for model in models:
        match = True
        
        if model.product_category and product.category != model.product_category:
            match = False
        if model.product_name_contains and model.product_name_contains.lower() not in product.name.lower():
            match = False
        if model.contact_type and contact.contact_type != model.contact_type:
            match = False
        
        if match:
            return model.analytical_account
    
    return None


@login_required
def purchase_order_list_view(request):
    orders = PurchaseOrder.objects.all().order_by('-date')
    return render(request, 'transactions/purchase_order_list.html', {'orders': orders})


@login_required
def purchase_order_create_view(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                po = form.save(commit=False)
                po.transaction_number = f"PO-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                po.created_by = request.user
                po.save()
                
                # Handle items
                product_ids = request.POST.getlist('product')
                quantities = request.POST.getlist('quantity')
                prices = request.POST.getlist('unit_price')
                
                for product_id, qty, price in zip(product_ids, quantities, prices):
                    if product_id and qty and price:
                        product = Product.objects.get(pk=product_id)
                        item = PurchaseOrderItem.objects.create(
                            purchase_order=po,
                            product=product,
                            quantity=qty,
                            unit_price=price,
                            analytical_account=apply_auto_analytical_model(None, po.contact, product) or po.analytical_account
                        )
                
                messages.success(request, 'Purchase Order created successfully!')
                return redirect('purchase_order_list')
    else:
        form = PurchaseOrderForm()
    
    products = Product.objects.filter(is_active=True)
    return render(request, 'transactions/purchase_order_form.html', {
        'form': form,
        'products': products,
        'title': 'Create Purchase Order'
    })


@login_required
def vendor_bill_list_view(request):
    bills = VendorBill.objects.all().order_by('-date')
    return render(request, 'transactions/vendor_bill_list.html', {'bills': bills})


@login_required
def vendor_bill_create_view(request):
    if request.method == 'POST':
        form = VendorBillForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                bill = form.save(commit=False)
                bill.transaction_number = f"VB-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                bill.created_by = request.user
                bill.save()
                
                # Handle items
                product_ids = request.POST.getlist('product')
                quantities = request.POST.getlist('quantity')
                prices = request.POST.getlist('unit_price')
                
                for product_id, qty, price in zip(product_ids, quantities, prices):
                    if product_id and qty and price:
                        product = Product.objects.get(pk=product_id)
                        item = VendorBillItem.objects.create(
                            vendor_bill=bill,
                            product=product,
                            quantity=qty,
                            unit_price=price,
                            analytical_account=apply_auto_analytical_model(None, bill.contact, product) or bill.analytical_account
                        )
                
                messages.success(request, 'Vendor Bill created successfully!')
                return redirect('vendor_bill_list')
    else:
        form = VendorBillForm()
    
    products = Product.objects.filter(is_active=True)
    return render(request, 'transactions/vendor_bill_form.html', {
        'form': form,
        'products': products,
        'title': 'Create Vendor Bill'
    })


@login_required
def vendor_bill_post_view(request, pk):
    bill = get_object_or_404(VendorBill, pk=pk)
    bill.status = 'posted'
    bill.save()
    messages.success(request, 'Vendor Bill posted successfully!')
    return redirect('vendor_bill_list')


@login_required
def sales_order_list_view(request):
    orders = SalesOrder.objects.all().order_by('-date')
    return render(request, 'transactions/sales_order_list.html', {'orders': orders})


@login_required
def sales_order_create_view(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                so = form.save(commit=False)
                so.transaction_number = f"SO-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                so.created_by = request.user
                so.save()
                
                # Handle items
                product_ids = request.POST.getlist('product')
                quantities = request.POST.getlist('quantity')
                prices = request.POST.getlist('unit_price')
                
                for product_id, qty, price in zip(product_ids, quantities, prices):
                    if product_id and qty and price:
                        product = Product.objects.get(pk=product_id)
                        item = SalesOrderItem.objects.create(
                            sales_order=so,
                            product=product,
                            quantity=qty,
                            unit_price=price,
                            analytical_account=apply_auto_analytical_model(None, so.contact, product) or so.analytical_account
                        )
                
                messages.success(request, 'Sales Order created successfully!')
                return redirect('sales_order_list')
    else:
        form = SalesOrderForm()
    
    products = Product.objects.filter(is_active=True)
    return render(request, 'transactions/sales_order_form.html', {
        'form': form,
        'products': products,
        'title': 'Create Sales Order'
    })


@login_required
def customer_invoice_list_view(request):
    invoices = CustomerInvoice.objects.all().order_by('-date')
    return render(request, 'transactions/customer_invoice_list.html', {'invoices': invoices})


@login_required
def customer_invoice_create_view(request):
    if request.method == 'POST':
        form = CustomerInvoiceForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.transaction_number = f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                invoice.created_by = request.user
                invoice.save()
                
                # Handle items
                product_ids = request.POST.getlist('product')
                quantities = request.POST.getlist('quantity')
                prices = request.POST.getlist('unit_price')
                
                for product_id, qty, price in zip(product_ids, quantities, prices):
                    if product_id and qty and price:
                        product = Product.objects.get(pk=product_id)
                        item = CustomerInvoiceItem.objects.create(
                            customer_invoice=invoice,
                            product=product,
                            quantity=qty,
                            unit_price=price,
                            analytical_account=apply_auto_analytical_model(None, invoice.contact, product) or invoice.analytical_account
                        )
                
                messages.success(request, 'Customer Invoice created successfully!')
                return redirect('customer_invoice_list')
    else:
        form = CustomerInvoiceForm()
    
    products = Product.objects.filter(is_active=True)
    return render(request, 'transactions/customer_invoice_form.html', {
        'form': form,
        'products': products,
        'title': 'Create Customer Invoice'
    })


@login_required
def customer_invoice_post_view(request, pk):
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    invoice.status = 'posted'
    invoice.save()
    messages.success(request, 'Customer Invoice posted successfully!')
    return redirect('customer_invoice_list')


@login_required
def payment_list_view(request):
    payments = Payment.objects.all().order_by('-date')
    return render(request, 'transactions/payment_list.html', {'payments': payments})


@login_required
def payment_create_view(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_number = f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            payment.created_by = request.user
            payment.save()
            messages.success(request, 'Payment recorded successfully!')
            return redirect('payment_list')
    else:
        form = PaymentForm()
    
    return render(request, 'transactions/payment_form.html', {
        'form': form,
        'title': 'Create Payment'
    })
