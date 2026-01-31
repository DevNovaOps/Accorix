# Stripe Webhook Setup Guide

## The Error You're Seeing

The errors in your logs indicate that:

1. **404 Error on `/webhook`**: Someone is trying to access a webhook endpoint that doesn't exist at the root level
2. **405 Error on `/payments/webhook/`**: GET requests are being made to the webhook endpoint, but webhooks only accept POST requests

## Correct Webhook Configuration

### 1. Webhook URL
Use this URL in your Stripe Dashboard:
```
https://yourdomain.com/payments/webhook/
```

For local development:
```
http://127.0.0.1:8000/payments/webhook/
```

### 2. Required Stripe Events
Configure your webhook to listen for these events:
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.succeeded`

### 3. Stripe Dashboard Setup

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Navigate to **Developers** → **Webhooks**
3. Click **Add endpoint**
4. Enter your webhook URL: `https://yourdomain.com/payments/webhook/`
5. Select the events listed above
6. Copy the **Webhook signing secret**
7. Update your `settings.py`:

```python
STRIPE_WEBHOOK_SECRET = 'whsec_your_actual_webhook_secret_here'
```

## Testing the Webhook

### Method 1: Using the Status Page
1. Visit: `http://127.0.0.1:8000/payments/webhook/status/`
2. Click "Test Webhook Endpoint"
3. Should show "✅ Webhook endpoint is working correctly!"

### Method 2: Using curl
```bash
# Test GET request (should return 405)
curl -X GET http://127.0.0.1:8000/payments/webhook/

# Test POST request (should return success)
curl -X POST http://127.0.0.1:8000/payments/webhook/test/ \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## Common Issues and Solutions

### Issue 1: 404 Error on `/webhook`
**Problem**: Old webhook URL configuration
**Solution**: Update webhook URL to `/payments/webhook/`

### Issue 2: 405 Method Not Allowed
**Problem**: GET requests to webhook endpoint
**Solution**: Webhooks must use POST method. Check if:
- Browser is accessing the URL directly (causes GET request)
- Stripe is configured correctly to send POST requests

### Issue 3: 400 Bad Request
**Problem**: Invalid signature or payload
**Solution**: 
- Verify webhook secret in settings.py
- Ensure payload is not modified in transit
- Check Content-Type header

## Security Notes

1. **Never expose webhook secrets** in version control
2. **Always verify webhook signatures** (already implemented)
3. **Use HTTPS in production** for webhook endpoints
4. **Implement idempotency** to handle duplicate events (already implemented)

## Debugging Webhook Issues

### Check Recent Webhook Events
If you're an admin user, visit the webhook status page to see recent webhook events and their processing status.

### Enable Webhook Logging
Add this to your Django settings for debugging:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'webhook.log',
        },
    },
    'loggers': {
        'payments.views': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Production Deployment

### 1. Use HTTPS
Stripe requires HTTPS for webhook endpoints in production.

### 2. Set Environment Variables
```bash
export STRIPE_PUBLISHABLE_KEY="pk_live_your_key"
export STRIPE_SECRET_KEY="sk_live_your_key"
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
```

### 3. Update Django Settings
```python
import os
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
```

## Testing Payment Flow

1. **Create a test invoice** in the portal
2. **Click "Pay with Card"** on the invoice
3. **Use Stripe test card**: `4242 4242 4242 4242`
4. **Complete payment** and verify webhook processing
5. **Check invoice status** - should update to "Paid"

The webhook errors you're seeing are normal during development and testing. The important thing is that the actual payment webhooks from Stripe work correctly when real payments are processed.