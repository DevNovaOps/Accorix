from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from transactions.models import CustomerInvoice, VendorBill, PurchaseOrder, SalesOrder, Payment
from core.models import Contact
from .forms import PaymentForm


@login_required
def portal_dashboard_view(request):
    """Portal user's dashboard showing their invoices, bills, and orders"""
    if request.user.role != 'portal':
        messages.error(request, 'Access denied. Portal users only.')
        return redirect('dashboard')
    
    try:
        contact = Contact.objects.get(email=request.user.email)
        
        invoices = CustomerInvoice.objects.filter(contact=contact, status='posted').order_by('-date')
        bills = VendorBill.objects.filter(contact=contact, status='posted').order_by('-date')
        purchase_orders = PurchaseOrder.objects.filter(contact=contact).order_by('-date')
        sales_orders = SalesOrder.objects.filter(contact=contact).order_by('-date')
        
        context = {
            'contact': contact,
            'invoices': invoices[:10],
            'bills': bills[:10],
            'purchase_orders': purchase_orders[:10],
            'sales_orders': sales_orders[:10],
        }
        
        return render(request, 'portal/dashboard.html', context)
    except Contact.DoesNotExist:
        messages.error(request, 'Contact not found. Please contact administrator.')
        return redirect('dashboard')


@login_required
def portal_invoices_view(request):
    if request.user.role != 'portal':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        contact = Contact.objects.get(email=request.user.email)
        invoices = CustomerInvoice.objects.filter(contact=contact, status='posted').order_by('-date')
        return render(request, 'portal/invoices.html', {'invoices': invoices})
    except Contact.DoesNotExist:
        messages.error(request, 'Contact not found.')
        return redirect('dashboard')


@login_required
def portal_bills_view(request):
    if request.user.role != 'portal':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        contact = Contact.objects.get(email=request.user.email)
        bills = VendorBill.objects.filter(contact=contact, status='posted').order_by('-date')
        return render(request, 'portal/bills.html', {'bills': bills})
    except Contact.DoesNotExist:
        messages.error(request, 'Contact not found.')
        return redirect('dashboard')


@login_required
def portal_orders_view(request):
    if request.user.role != 'portal':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        contact = Contact.objects.get(email=request.user.email)
        purchase_orders = PurchaseOrder.objects.filter(contact=contact).order_by('-date')
        sales_orders = SalesOrder.objects.filter(contact=contact).order_by('-date')
        return render(request, 'portal/orders.html', {
            'purchase_orders': purchase_orders,
            'sales_orders': sales_orders
        })
    except Contact.DoesNotExist:
        messages.error(request, 'Contact not found.')
        return redirect('dashboard')


@login_required
def portal_invoice_detail_view(request, pk):
    if request.user.role != 'portal':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    
    # Verify ownership
    try:
        contact = Contact.objects.get(email=request.user.email)
        if invoice.contact != contact:
            messages.error(request, 'Access denied.')
            return redirect('portal_dashboard')
    except Contact.DoesNotExist:
        messages.error(request, 'Contact not found.')
        return redirect('dashboard')
    
    return render(request, 'portal/invoice_detail.html', {'invoice': invoice})


@login_required
def portal_bill_detail_view(request, pk):
    if request.user.role != 'portal':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    bill = get_object_or_404(VendorBill, pk=pk)
    
    # Verify ownership
    try:
        contact = Contact.objects.get(email=request.user.email)
        if bill.contact != contact:
            messages.error(request, 'Access denied.')
            return redirect('portal_dashboard')
    except Contact.DoesNotExist:
        messages.error(request, 'Contact not found.')
        return redirect('dashboard')
    
    return render(request, 'portal/bill_detail.html', {'bill': bill})


@login_required
def portal_payment_view(request, invoice_id=None, bill_id=None):
    if request.user.role != 'portal':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        contact = Contact.objects.get(email=request.user.email)
        
        if request.method == 'POST':
            form = PaymentForm(request.POST)
            if form.is_valid():
                payment = form.save(commit=False)
                payment.payment_method = 'online'  # Portal payments are online
                payment.created_by = request.user
                payment.save()
                messages.success(request, 'Payment submitted successfully!')
                return redirect('portal_dashboard')
        else:
            initial = {}
            if invoice_id:
                invoice = get_object_or_404(CustomerInvoice, pk=invoice_id)
                if invoice.contact == contact:
                    initial['customer_invoice'] = invoice
                    initial['amount'] = invoice.remaining_amount
            elif bill_id:
                bill = get_object_or_404(VendorBill, pk=bill_id)
                if bill.contact == contact:
                    initial['vendor_bill'] = bill
                    initial['amount'] = bill.remaining_amount
            
            form = PaymentForm(initial=initial)
            form.fields['customer_invoice'].queryset = CustomerInvoice.objects.filter(
                contact=contact, status='posted', payment_status__in=['not_paid', 'partially_paid']
            )
            form.fields['vendor_bill'].queryset = VendorBill.objects.filter(
                contact=contact, status='posted', payment_status__in=['not_paid', 'partially_paid']
            )
        
        return render(request, 'portal/payment.html', {'form': form})
    except Contact.DoesNotExist:
        messages.error(request, 'Contact not found.')
        return redirect('dashboard')
