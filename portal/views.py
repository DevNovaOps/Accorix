from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from transactions.models import CustomerInvoice, VendorBill, PurchaseOrder, SalesOrder, Payment
from transactions.views import generate_invoice_pdf, generate_bill_pdf
from core.models import Contact
from core.decorators import portal_user_required, customer_required, vendor_required
from .forms import PaymentForm


@login_required
@portal_user_required
def portal_dashboard_view(request):
    """Portal user's dashboard showing their invoices, bills, and orders"""
    contact = request.user.contact
    if not contact:
        messages.error(request, 'Contact profile not found. Please contact administrator.')
        return redirect('dashboard')
    
    # Get data based on user role
    context = {'contact': contact}
    
    if request.user.role == 'customer':
        # Customers see their invoices and sales orders
        invoices = CustomerInvoice.objects.filter(contact=contact, status='posted').order_by('-date')
        sales_orders = SalesOrder.objects.filter(contact=contact).order_by('-date')
        context.update({
            'invoices': invoices[:10],
            'sales_orders': sales_orders[:10],
            'total_outstanding': sum(inv.remaining_amount for inv in invoices if inv.payment_status != 'paid'),
        })
    
    elif request.user.role == 'vendor':
        # Vendors see their bills and purchase orders
        bills = VendorBill.objects.filter(contact=contact, status='posted').order_by('-date')
        purchase_orders = PurchaseOrder.objects.filter(contact=contact).order_by('-date')
        context.update({
            'bills': bills[:10],
            'purchase_orders': purchase_orders[:10],
            'total_receivable': sum(bill.remaining_amount for bill in bills if bill.payment_status != 'paid'),
        })
    
    return render(request, 'portal/dashboard.html', context)


@login_required
@customer_required
def portal_invoices_view(request):
    """Customer invoices view - only for customers"""
    contact = request.user.contact
    if not contact:
        messages.error(request, 'Contact profile not found.')
        return redirect('dashboard')
    
    invoices = CustomerInvoice.objects.filter(contact=contact, status='posted').order_by('-date')
    return render(request, 'portal/invoices.html', {'invoices': invoices})


@login_required
@vendor_required
def portal_bills_view(request):
    """Vendor bills view - only for vendors"""
    contact = request.user.contact
    if not contact:
        messages.error(request, 'Contact profile not found.')
        return redirect('dashboard')
    
    bills = VendorBill.objects.filter(contact=contact, status='posted').order_by('-date')
    return render(request, 'portal/bills.html', {'bills': bills})


@login_required
@portal_user_required
def portal_orders_view(request):
    """Orders view for both customers and vendors"""
    contact = request.user.contact
    if not contact:
        messages.error(request, 'Contact profile not found.')
        return redirect('dashboard')
    
    context = {'contact': contact}
    
    if request.user.role == 'customer':
        sales_orders = SalesOrder.objects.filter(contact=contact).order_by('-date')
        context['sales_orders'] = sales_orders
    elif request.user.role == 'vendor':
        purchase_orders = PurchaseOrder.objects.filter(contact=contact).order_by('-date')
        context['purchase_orders'] = purchase_orders
    
    return render(request, 'portal/orders.html', context)


@login_required
@customer_required
def portal_invoice_detail_view(request, pk):
    """Invoice detail view - only for customers"""
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    
    # Verify ownership
    if invoice.contact != request.user.contact:
        messages.error(request, 'Access denied.')
        return redirect('portal_dashboard')
    
    return render(request, 'portal/invoice_detail.html', {'invoice': invoice})


@login_required
@vendor_required
def portal_bill_detail_view(request, pk):
    """Bill detail view - only for vendors"""
    bill = get_object_or_404(VendorBill, pk=pk)
    
    # Verify ownership
    if bill.contact != request.user.contact:
        messages.error(request, 'Access denied.')
        return redirect('portal_dashboard')
    
    return render(request, 'portal/bill_detail.html', {'bill': bill})


@login_required
@portal_user_required
def portal_payment_view(request, invoice_id=None, bill_id=None):
    """Payment view for portal users"""
    contact = request.user.contact
    if not contact:
        messages.error(request, 'Contact profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_method = 'stripe'  # Portal payments are stripe
            payment.created_by = request.user
            payment.save()
            messages.success(request, 'Payment submitted successfully!')
            return redirect('portal_dashboard')
    else:
        initial = {}
        if invoice_id and request.user.role == 'customer':
            invoice = get_object_or_404(CustomerInvoice, pk=invoice_id)
            if invoice.contact == contact:
                initial['customer_invoice'] = invoice
                initial['amount'] = invoice.remaining_amount
        elif bill_id and request.user.role == 'vendor':
            bill = get_object_or_404(VendorBill, pk=bill_id)
            if bill.contact == contact:
                initial['vendor_bill'] = bill
                initial['amount'] = bill.remaining_amount
        
        form = PaymentForm(initial=initial)
        
        # Filter form fields based on user role
        if request.user.role == 'customer':
            form.fields['customer_invoice'].queryset = CustomerInvoice.objects.filter(
                contact=contact, status='posted', payment_status__in=['not_paid', 'partially_paid']
            )
            form.fields['vendor_bill'].queryset = VendorBill.objects.none()
        elif request.user.role == 'vendor':
            form.fields['vendor_bill'].queryset = VendorBill.objects.filter(
                contact=contact, status='posted', payment_status__in=['not_paid', 'partially_paid']
            )
            form.fields['customer_invoice'].queryset = CustomerInvoice.objects.none()
    
    return render(request, 'portal/payment.html', {'form': form})


@login_required
@customer_required
def portal_invoice_pdf(request, pk):
    """Generate PDF for customer invoice - portal access"""
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    
    # Verify ownership
    if invoice.contact != request.user.contact:
        messages.error(request, 'Access denied.')
        return redirect('portal_dashboard')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.transaction_number}.pdf"'
    
    # Generate PDF
    generate_invoice_pdf(response, invoice)
    
    return response


@login_required
@vendor_required
def portal_bill_pdf(request, pk):
    """Generate PDF for vendor bill - portal access"""
    bill = get_object_or_404(VendorBill, pk=pk)
    
    # Verify ownership
    if bill.contact != request.user.contact:
        messages.error(request, 'Access denied.')
        return redirect('portal_dashboard')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bill_{bill.transaction_number}.pdf"'
    
    # Generate PDF
    generate_bill_pdf(response, bill)
    
    return response