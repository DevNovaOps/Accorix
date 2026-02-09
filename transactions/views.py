from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from datetime import date
import json
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from .models import (
    PurchaseOrder, VendorBill, SalesOrder, CustomerInvoice, Payment, ChartOfAccounts,
    PurchaseOrderItem, VendorBillItem, SalesOrderItem, CustomerInvoiceItem
)
from core.models import Contact, Product, AnalyticalAccount, AutoAnalyticalModel
from .forms import (
    PurchaseOrderForm, VendorBillForm, SalesOrderForm, CustomerInvoiceForm, PaymentForm,
    ChartOfAccountsForm, BudgetOverrideForm, PurchaseOrderItemFormSet, VendorBillItemFormSet,
    SalesOrderItemFormSet, CustomerInvoiceItemFormSet
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
        formset = PurchaseOrderItemFormSet(request.POST)
        
        # Check for budget override
        budget_override_form = None
        if 'budget_override' in request.POST:
            budget_override_form = BudgetOverrideForm(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                po = form.save(commit=False)
                po.created_by = request.user
                po.save()
                
                formset.instance = po
                items = formset.save()
                
                # Validate budget
                budget_validation = po.validate_budget()
                
                if budget_validation['status'] == 'exceeds_budget' and not po.budget_override:
                    if budget_override_form and budget_override_form.is_valid():
                        po.budget_override = True
                        po.budget_override_reason = budget_override_form.cleaned_data['override_reason']
                        po.save()
                        messages.warning(request, f"Budget exceeded by ₹{budget_validation['exceeds_by']:,.2f} but override approved.")
                    else:
                        # Show budget warning
                        return render(request, 'transactions/purchase_order_form.html', {
                            'form': form,
                            'formset': formset,
                            'budget_warning': budget_validation,
                            'budget_override_form': BudgetOverrideForm(),
                            'title': 'Create Purchase Order'
                        })
                
                messages.success(request, 'Purchase Order created successfully!')
                return redirect('purchase_order_list')
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet()
    
    return render(request, 'transactions/purchase_order_form.html', {
        'form': form,
        'formset': formset,
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
        formset = VendorBillItemFormSet(request.POST)
        
        # Check for budget override
        budget_override_form = None
        if 'budget_override' in request.POST:
            budget_override_form = BudgetOverrideForm(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                bill = form.save(commit=False)
                bill.created_by = request.user
                bill.save()
                
                formset.instance = bill
                items = formset.save()
                
                # Validate budget
                budget_validation = bill.validate_budget()
                
                if budget_validation['status'] == 'exceeds_budget' and not bill.budget_override:
                    if budget_override_form and budget_override_form.is_valid():
                        bill.budget_override = True
                        bill.budget_override_reason = budget_override_form.cleaned_data['override_reason']
                        bill.save()
                        messages.warning(request, f"Budget exceeded by ₹{budget_validation['exceeds_by']:,.2f} but override approved.")
                    else:
                        # Show budget warning
                        return render(request, 'transactions/vendor_bill_form.html', {
                            'form': form,
                            'formset': formset,
                            'budget_warning': budget_validation,
                            'budget_override_form': BudgetOverrideForm(),
                            'title': 'Create Vendor Bill'
                        })
                
                messages.success(request, 'Vendor Bill created successfully!')
                return redirect('vendor_bill_list')
    else:
        form = VendorBillForm()
        formset = VendorBillItemFormSet()
    
    return render(request, 'transactions/vendor_bill_form.html', {
        'form': form,
        'formset': formset,
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


# Chart of Accounts Views
@login_required
@user_passes_test(is_admin)
def chart_of_accounts_list_view(request):
    accounts = ChartOfAccounts.objects.all().order_by('account_code')
    return render(request, 'transactions/chart_of_accounts_list.html', {'accounts': accounts})


@login_required
@user_passes_test(is_admin)
def chart_of_accounts_create_view(request):
    if request.method == 'POST':
        form = ChartOfAccountsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chart of Account created successfully!')
            return redirect('chart_of_accounts_list')
    else:
        form = ChartOfAccountsForm()
    
    return render(request, 'transactions/chart_of_accounts_form.html', {
        'form': form,
        'title': 'Create Chart of Account'
    })


@login_required
@user_passes_test(is_admin)
def chart_of_accounts_edit_view(request, pk):
    account = get_object_or_404(ChartOfAccounts, pk=pk)
    if request.method == 'POST':
        form = ChartOfAccountsForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chart of Account updated successfully!')
            return redirect('chart_of_accounts_list')
    else:
        form = ChartOfAccountsForm(instance=account)
    
    return render(request, 'transactions/chart_of_accounts_form.html', {
        'form': form,
        'title': 'Edit Chart of Account'
    })


# Bill Payment Views
@login_required
def bill_payment_list_view(request):
    """List all unpaid bills for payment processing"""
    unpaid_bills = VendorBill.objects.filter(
        status='posted',
        payment_status__in=['not_paid', 'partially_paid']
    ).order_by('-date')
    
    return render(request, 'transactions/bill_payment_list.html', {
        'bills': unpaid_bills,
        'title': 'Bill Payments'
    })


@login_required
def bill_payment_create_view(request, bill_id):
    """Create payment for a specific bill"""
    bill = get_object_or_404(VendorBill, pk=bill_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.vendor_bill = bill
            payment.created_by = request.user
            
            # Validate payment amount
            if payment.amount > bill.remaining_amount:
                messages.error(request, f'Payment amount cannot exceed remaining balance of ₹{bill.remaining_amount:,.2f}')
                return render(request, 'transactions/bill_payment_form.html', {
                    'form': form,
                    'bill': bill,
                    'title': f'Pay Bill {bill.transaction_number}'
                })
            
            payment.save()
            messages.success(request, f'Payment of ₹{payment.amount:,.2f} recorded successfully!')
            return redirect('bill_payment_list')
    else:
        form = PaymentForm(initial={
            'date': date.today(),
            'amount': bill.remaining_amount
        })
    
    return render(request, 'transactions/bill_payment_form.html', {
        'form': form,
        'bill': bill,
        'title': f'Pay Bill {bill.transaction_number}'
    })


# Stripe Payment Views
@login_required
def stripe_payment_view(request, invoice_id):
    """Create Stripe payment for customer invoice"""
    invoice = get_object_or_404(CustomerInvoice, pk=invoice_id)
    
    if request.method == 'POST':
        try:
            import stripe
            from django.conf import settings
            
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(invoice.remaining_amount * 100),  # Convert to cents
                currency='inr',
                metadata={
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.transaction_number
                }
            )
            
            # Create payment record
            from payments.models import StripePayment
            stripe_payment = StripePayment.objects.create(
                stripe_payment_intent_id=intent.id,
                amount=invoice.remaining_amount,
                customer_invoice=invoice,
                user=request.user,
                description=f'Payment for Invoice {invoice.transaction_number}'
            )
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'payment_id': stripe_payment.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'payments/stripe_payment.html', {
        'invoice': invoice,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    })


# AJAX Views for dynamic forms
@login_required
def get_product_price(request):
    """Get product price for dynamic form updates"""
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            product = Product.objects.get(pk=product_id)
            return JsonResponse({
                'unit_price': float(product.unit_price),
                'sale_price': float(product.sale_price) if product.sale_price else None,
                'purchase_price': float(product.purchase_price) if product.purchase_price else None
            })
        except Product.DoesNotExist:
            pass
    
    return JsonResponse({'error': 'Product not found'}, status=404)


@login_required
def validate_budget_ajax(request):
    """AJAX endpoint for budget validation"""
    if request.method == 'POST':
        data = json.loads(request.body)
        analytical_account_id = data.get('analytical_account_id')
        amount = data.get('amount')
        date_str = data.get('date')
        
        if analytical_account_id and amount and date_str:
            try:
                from budgets.models import Budget
                from datetime import datetime
                
                analytical_account = AnalyticalAccount.objects.get(pk=analytical_account_id)
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Get active budgets
                budgets = Budget.objects.filter(
                    analytical_account=analytical_account,
                    status='confirmed',
                    start_date__lte=transaction_date,
                    end_date__gte=transaction_date,
                    is_active=True
                )
                
                if budgets.exists():
                    budget = budgets.first()
                    if budget.actual_amount + float(amount) > budget.budgeted_amount:
                        exceeds_by = (budget.actual_amount + float(amount)) - budget.budgeted_amount
                        return JsonResponse({
                            'status': 'exceeds_budget',
                            'message': f'Exceeds approved budget by ₹{exceeds_by:,.2f}',
                            'budget_name': budget.name,
                            'budgeted_amount': float(budget.budgeted_amount),
                            'actual_amount': float(budget.actual_amount),
                            'exceeds_by': float(exceeds_by)
                        })
                    else:
                        return JsonResponse({
                            'status': 'within_budget',
                            'message': 'Within budget limits'
                        })
                else:
                    return JsonResponse({
                        'status': 'no_budget',
                        'message': 'No active budget found for this analytical account'
                    })
                    
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# PDF Generation Views
@login_required
def customer_invoice_pdf(request, pk):
    """Generate PDF for customer invoice"""
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    
    # Check permissions
    if not request.user.role == 'admin' and invoice.contact != getattr(request.user, 'contact', None):
        if request.user.role not in ['admin', 'invoicing']:
            messages.error(request, 'Access denied.')
            return redirect('customer_invoice_list')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.transaction_number}.pdf"'
    
    # Generate PDF
    generate_invoice_pdf(response, invoice)
    
    return response


@login_required
def vendor_bill_pdf(request, pk):
    """Generate PDF for vendor bill"""
    bill = get_object_or_404(VendorBill, pk=pk)
    
    # Check permissions
    if not request.user.role == 'admin' and bill.contact != getattr(request.user, 'contact', None):
        if request.user.role not in ['admin', 'invoicing']:
            messages.error(request, 'Access denied.')
            return redirect('vendor_bill_list')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bill_{bill.transaction_number}.pdf"'
    
    # Generate PDF
    generate_bill_pdf(response, bill)
    
    return response


def generate_invoice_pdf(response, invoice):
    """Generate professional PDF content for customer invoice"""
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define professional styles
    styles = getSampleStyleSheet()
    
    # Custom styles for professional invoice
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=3,
        textColor=colors.HexColor('#1a365d'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    invoice_title_style = ParagraphStyle(
        'InvoiceTitleStyle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=20,
        textColor=colors.HexColor('#00BCD4'),
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold'
    )
    
    # Header section with company info and invoice title
    company_info = """<b>ACCORIX</b><br/>
    Finance OS - Complete Accounting Solution"""
    
    header_data = [
        [
            Paragraph(company_info, company_style),
            Paragraph("INVOICE", invoice_title_style)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[4*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    elements.append(header_table)
    
    # Professional separator line
    line_data = [['']]
    line_table = Table(line_data, colWidths=[7.5*inch])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 3, colors.HexColor('#00BCD4')),
        ('TOPPADDING', (0, 0), (-1, 0), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 20),
    ]))
    elements.append(line_table)
    
    # Company and Customer Address Section
    company_address = """<b>ACCORIX SYSTEMS PVT LTD</b><br/>
    123 Business Park, Tech City<br/>
    Mumbai, Maharashtra 400001<br/>
    Phone: +91 22 1234 5678<br/>
    Email: info@accorix.com<br/>
    GST: 27ABCDE1234F1Z5"""
    
    customer_address = f"""<b>BILL TO:</b><br/>
    <b>{invoice.contact.name}</b><br/>
    {invoice.contact.address or 'Address not provided'}<br/>
    Phone: {invoice.contact.phone or 'Not provided'}<br/>
    Email: {invoice.contact.email or 'Not provided'}"""
    
    address_data = [
        [
            Paragraph(company_address, styles['Normal']),
            Paragraph(customer_address, styles['Normal'])
        ]
    ]
    
    address_table = Table(address_data, colWidths=[3.75*inch, 3.75*inch])
    address_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
    ]))
    
    elements.append(address_table)
    
    # Invoice Details Section
    invoice_details_data = [
        ['Invoice Number:', invoice.transaction_number, 'Invoice Date:', invoice.date.strftime('%d %B %Y')],
        ['Invoice ID:', invoice.invoice_number or 'N/A', 'Due Date:', invoice.due_date.strftime('%d %B %Y')],
        ['Payment Status:', invoice.get_payment_status_display(), 'Amount Due:', f"₹ {invoice.remaining_amount:,.2f}"],
    ]
    
    invoice_details_table = Table(invoice_details_data, colWidths=[1.2*inch, 2.6*inch, 1.2*inch, 2.5*inch])
    invoice_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f7fafc')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(invoice_details_table)
    elements.append(Spacer(1, 30))
    
    # Items Table with Professional Design
    items_data = [['#', 'DESCRIPTION', 'QTY', 'RATE', 'AMOUNT']]
    
    # Add items
    for i, item in enumerate(invoice.items.all(), 1):
        items_data.append([
            str(i),
            item.product.name,
            f"{int(item.quantity)}",
            f"₹ {item.unit_price:,.2f}",
            f"₹ {item.line_total:,.2f}"
        ])
    
    # Calculate totals
    subtotal = sum(item.line_total for item in invoice.items.all())
    tax_amount = float(subtotal) * 0.18  # 18% GST
    total_amount = float(subtotal) + tax_amount
    
    items_table = Table(items_data, colWidths=[0.5*inch, 3.8*inch, 0.7*inch, 1.3*inch, 1.7*inch])
    items_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),   # # header
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),     # DESCRIPTION header
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),   # QTY header
        ('ALIGN', (3, 0), (3, 0), 'RIGHT'),    # RATE header
        ('ALIGN', (4, 0), (4, 0), 'RIGHT'),    # AMOUNT header
        
        # Data rows alignment
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item number - center
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description - left
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Quantity - center
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Rate - right
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Amount - right
        
        # Borders and padding
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Summary Section - Connected columns
    summary_data = [
        ['', '', 'Subtotal:', f"₹ {subtotal:,.2f}"],
        ['', '', 'GST (18%):', f"₹ {tax_amount:,.2f}"],
        ['', '', 'TOTAL AMOUNT:', f"₹ {total_amount:,.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[0.5*inch, 3.8*inch, 1.5*inch, 2.2*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 13),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Labels - right aligned
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),   # Values - right aligned
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#00BCD4')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('GRID', (2, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 40))
    
    # Terms and Conditions
    terms_text = """<b>Terms & Conditions:</b><br/>
    1. Payment is due within 30 days of invoice date.<br/>
    2. Late payments may incur additional charges.<br/>
    3. All disputes must be reported within 7 days.<br/>
    4. This invoice is computer generated and does not require signature."""
    
    elements.append(Paragraph(terms_text, styles['Normal']))
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_text = """<b>Thank you for your business!</b><br/>
    For any queries, contact us at info@accorix.com or +91 22 1234 5678"""
    
    footer_para = Paragraph(footer_text, ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#4a5568'),
        alignment=TA_CENTER
    ))
    
    elements.append(footer_para)
    
    # Build PDF
    doc.build(elements)


def generate_bill_pdf(response, bill):
    """Generate professional PDF content for vendor bill"""
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define professional styles
    styles = getSampleStyleSheet()
    
    # Custom styles for professional bill
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=3,
        textColor=colors.HexColor('#1a365d'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    bill_title_style = ParagraphStyle(
        'BillTitleStyle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=20,
        textColor=colors.HexColor('#E91E63'),
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold'
    )
    
    # Header section with company info and bill title
    company_info = """<b>ACCORIX</b><br/>
    Finance OS - Complete Accounting Solution"""
    
    header_data = [
        [
            Paragraph(company_info, company_style),
            Paragraph("BILL", bill_title_style)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[4*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    elements.append(header_table)
    
    # Professional separator line
    line_data = [['']]
    line_table = Table(line_data, colWidths=[7.5*inch])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 3, colors.HexColor('#E91E63')),
        ('TOPPADDING', (0, 0), (-1, 0), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 20),
    ]))
    elements.append(line_table)
    
    # Company and Vendor Address Section
    company_address = """<b>ACCORIX SYSTEMS PVT LTD</b><br/>
    123 Business Park, Tech City<br/>
    Mumbai, Maharashtra 400001<br/>
    Phone: +91 22 1234 5678<br/>
    Email: info@accorix.com<br/>
    GST: 27ABCDE1234F1Z5"""
    
    vendor_address = f"""<b>VENDOR:</b><br/>
    <b>{bill.contact.name}</b><br/>
    {bill.contact.address or 'Address not provided'}<br/>
    Phone: {bill.contact.phone or 'Not provided'}<br/>
    Email: {bill.contact.email or 'Not provided'}"""
    
    address_data = [
        [
            Paragraph(company_address, styles['Normal']),
            Paragraph(vendor_address, styles['Normal'])
        ]
    ]
    
    address_table = Table(address_data, colWidths=[3.75*inch, 3.75*inch])
    address_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
    ]))
    
    elements.append(address_table)
    
    # Bill Details Section
    bill_details_data = [
        ['Bill Number:', bill.transaction_number, 'Bill Date:', bill.date.strftime('%d %B %Y')],
        ['Bill ID:', bill.bill_number or 'N/A', 'Due Date:', bill.due_date.strftime('%d %B %Y')],
        ['Payment Status:', bill.get_payment_status_display(), 'Amount Due:', f"Rs {bill.remaining_amount:,.2f}"],
    ]
    
    bill_details_table = Table(bill_details_data, colWidths=[1.2*inch, 2.6*inch, 1.2*inch, 2.5*inch])
    bill_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f7fafc')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(bill_details_table)
    elements.append(Spacer(1, 30))
    
    # Items Table with Professional Design
    items_data = [['#', 'DESCRIPTION', 'QTY', 'RATE', 'AMOUNT']]
    
    # Add items
    for i, item in enumerate(bill.items.all(), 1):
        items_data.append([
            str(i),
            item.product.name,
            f"{int(item.quantity)}",
            f"₹ {item.unit_price:,.2f}",
            f"₹ {item.line_total:,.2f}"
        ])
    
    # Calculate totals
    subtotal = sum(item.line_total for item in bill.items.all())
    tax_amount = float(subtotal) * 0.18  # 18% GST
    total_amount = float(subtotal) + tax_amount
    
    items_table = Table(items_data, colWidths=[0.5*inch, 3.8*inch, 0.7*inch, 1.3*inch, 1.7*inch])
    items_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),   # # header
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),     # DESCRIPTION header
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),   # QTY header
        ('ALIGN', (3, 0), (3, 0), 'RIGHT'),    # RATE header
        ('ALIGN', (4, 0), (4, 0), 'RIGHT'),    # AMOUNT header
        
        # Data rows alignment
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item number - center
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description - left
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Quantity - center
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Rate - right
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Amount - right
        
        # Borders and padding
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Summary Section - Connected columns
    summary_data = [
        ['', '', 'Subtotal:', f"Rs {subtotal:,.2f}"],
        ['', '', 'GST (18%):', f"Rs {tax_amount:,.2f}"],
        ['', '', 'TOTAL AMOUNT:', f"Rs {total_amount:,.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[0.5*inch, 3.8*inch, 1.5*inch, 2.2*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 13),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Labels - right aligned
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),   # Values - right aligned
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E91E63')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('GRID', (2, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 40))
    
    # Terms and Conditions
    terms_text = """<b>Terms & Conditions:</b><br/>
    1. Payment is due within 30 days of bill date.<br/>
    2. Late payments may incur additional charges.<br/>
    3. All disputes must be reported within 7 days.<br/>
    4. This bill is computer generated and does not require signature."""
    
    elements.append(Paragraph(terms_text, styles['Normal']))
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_text = """<b>Thank you for your service!</b><br/>
    For any queries, contact us at info@accorix.com or +91 22 1234 5678"""
    
    footer_para = Paragraph(footer_text, ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#4a5568'),
        alignment=TA_CENTER
    ))
    
    elements.append(footer_para)
    
    # Build PDF
    doc.build(elements)