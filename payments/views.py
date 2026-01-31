import json
import stripe
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.utils import timezone

from core.decorators import portal_user_required
from transactions.models import CustomerInvoice, VendorBill, Payment
from .models import StripePayment, PaymentWebhook

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
@portal_user_required
def create_payment_intent(request):
    """Create Stripe Payment Intent for invoice payment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            invoice_id = data.get('invoice_id')
            amount = data.get('amount')
            
            if not invoice_id or not amount:
                return JsonResponse({'error': 'Missing invoice_id or amount'}, status=400)
            
            # Get the invoice and verify ownership
            invoice = get_object_or_404(CustomerInvoice, pk=invoice_id)
            if invoice.contact != request.user.contact:
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            # Convert amount to paise (Stripe uses smallest currency unit)
            amount_in_paise = int(float(amount) * 100)
            
            # Create Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=amount_in_paise,
                currency='inr',
                metadata={
                    'invoice_id': invoice_id,
                    'user_id': request.user.id,
                    'invoice_number': invoice.transaction_number,
                },
                description=f'Payment for Invoice {invoice.transaction_number}',
            )
            
            # Save payment record
            stripe_payment = StripePayment.objects.create(
                stripe_payment_intent_id=intent.id,
                amount=amount,
                customer_invoice=invoice,
                user=request.user,
                description=f'Payment for Invoice {invoice.transaction_number}',
                metadata={
                    'invoice_id': invoice_id,
                    'invoice_number': invoice.transaction_number,
                }
            )
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'payment_id': stripe_payment.id,
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@portal_user_required
def payment_page(request, invoice_id):
    """Payment page with Stripe Elements"""
    invoice = get_object_or_404(CustomerInvoice, pk=invoice_id)
    
    # Verify ownership
    if invoice.contact != request.user.contact:
        messages.error(request, 'Access denied.')
        return redirect('portal_dashboard')
    
    # Check if invoice is already paid
    if invoice.payment_status == 'paid':
        messages.info(request, 'This invoice is already paid.')
        return redirect('portal_invoice_detail', pk=invoice_id)
    
    context = {
        'invoice': invoice,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'amount': invoice.remaining_amount,
    }
    
    return render(request, 'payments/payment_page.html', context)


@login_required
@portal_user_required
def payment_success(request, payment_id):
    """Payment success page"""
    stripe_payment = get_object_or_404(StripePayment, pk=payment_id, user=request.user)
    
    context = {
        'payment': stripe_payment,
        'invoice': stripe_payment.customer_invoice,
    }
    
    return render(request, 'payments/payment_success.html', context)


@login_required
@portal_user_required
def payment_cancel(request, payment_id):
    """Payment canceled page"""
    stripe_payment = get_object_or_404(StripePayment, pk=payment_id, user=request.user)
    
    # Update payment status
    stripe_payment.status = 'canceled'
    stripe_payment.save()
    
    context = {
        'payment': stripe_payment,
        'invoice': stripe_payment.customer_invoice,
    }
    
    return render(request, 'payments/payment_cancel.html', context)


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not sig_header:
        return JsonResponse({'error': 'Missing signature header'}, status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Save webhook event
    webhook, created = PaymentWebhook.objects.get_or_create(
        stripe_event_id=event['id'],
        defaults={
            'event_type': event['type'],
            'data': event['data'],
        }
    )
    
    if webhook.processed:
        return JsonResponse({'status': 'already processed'}, status=200)
    
    # Handle the event
    try:
        if event['type'] == 'payment_intent.succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'payment_intent.payment_failed':
            handle_payment_failed(event['data']['object'])
        elif event['type'] == 'charge.succeeded':
            handle_charge_succeeded(event['data']['object'])
        
        # Mark webhook as processed
        webhook.processed = True
        webhook.save()
        
        return JsonResponse({'status': 'success'}, status=200)
        
    except Exception as e:
        return JsonResponse({'error': f'Processing failed: {str(e)}'}, status=500)


def handle_payment_succeeded(payment_intent):
    """Handle successful payment"""
    try:
        stripe_payment = StripePayment.objects.get(
            stripe_payment_intent_id=payment_intent['id']
        )
        
        # Update payment status
        stripe_payment.status = 'succeeded'
        stripe_payment.paid_at = timezone.now()
        stripe_payment.save()
        
        # Create payment record in transactions
        if stripe_payment.customer_invoice:
            Payment.objects.create(
                payment_number=f'STRIPE-{stripe_payment.id}',
                date=timezone.now().date(),
                amount=stripe_payment.amount,
                payment_method='online',
                reference=stripe_payment.stripe_payment_intent_id,
                customer_invoice=stripe_payment.customer_invoice,
                created_by=stripe_payment.user,
                notes=f'Stripe payment for invoice {stripe_payment.customer_invoice.transaction_number}',
            )
            
            # Update invoice payment status
            stripe_payment.customer_invoice.update_payment_status()
        
    except StripePayment.DoesNotExist:
        pass


def handle_payment_failed(payment_intent):
    """Handle failed payment"""
    try:
        stripe_payment = StripePayment.objects.get(
            stripe_payment_intent_id=payment_intent['id']
        )
        stripe_payment.status = 'failed'
        stripe_payment.save()
    except StripePayment.DoesNotExist:
        pass


def handle_charge_succeeded(charge):
    """Handle successful charge"""
    try:
        stripe_payment = StripePayment.objects.get(
            stripe_payment_intent_id=charge['payment_intent']
        )
        stripe_payment.stripe_charge_id = charge['id']
        stripe_payment.save()
    except StripePayment.DoesNotExist:
        pass


@csrf_exempt
def webhook_test(request):
    """Test endpoint for webhook connectivity"""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'Webhook endpoint is active',
            'method': 'POST required for actual webhooks',
            'endpoint': '/payments/webhook/'
        })
    elif request.method == 'POST':
        return JsonResponse({
            'status': 'Test webhook received',
            'headers': dict(request.META),
            'body_length': len(request.body)
        })
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def webhook_status(request):
    """Webhook status and configuration page"""
    recent_webhooks = PaymentWebhook.objects.all()[:10] if request.user.is_superuser else []
    
    context = {
        'recent_webhooks': recent_webhooks,
    }
    
    return render(request, 'payments/webhook_status.html', context)


@login_required
def payment_history(request):
    """View payment history"""
    payments = StripePayment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'payments/payment_history.html', context)