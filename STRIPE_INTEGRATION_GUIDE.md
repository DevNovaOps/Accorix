# 🔥 **STRIPE INTEGRATION GUIDE - ACCORIX ERP**

## 📋 **Table of Contents**
1. [Prerequisites](#prerequisites)
2. [Stripe Account Setup](#stripe-account-setup)
3. [Environment Configuration](#environment-configuration)
4. [Testing the Integration](#testing-the-integration)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 **1. PREREQUISITES**

### System Requirements
- ✅ Python 3.8+
- ✅ Django 4.2+
- ✅ Stripe Python library (`stripe==7.8.0`)
- ✅ SSL certificate (for production webhooks)
- ✅ Domain name (for production)

### Current System Status
```bash
# Verify current installation
pip list | grep stripe
# Should show: stripe==7.8.0
```

---

## 🏦 **2. STRIPE ACCOUNT SETUP**

### Step 1: Create Stripe Account
1. **Visit**: https://dashboard.stripe.com/register
2. **Sign up** with business email
3. **Verify email** and complete business information
4. **Enable Indian market** (for INR support)

### Step 2: Get API Keys
1. **Login** to Stripe Dashboard
2. **Navigate**: Developers → API Keys
3. **Copy these keys**:
   ```
   Publishable Key: pk_test_... (for frontend)
   Secret Key: sk_test_... (for backend)
   ```

### Step 3: Configure Webhooks
1. **Navigate**: Developers → Webhooks
2. **Click**: "Add endpoint"
3. **Endpoint URL**: `https://yourdomain.com/payments/webhook/`
4. **Select Events**:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
   - `charge.dispute.created`

### Step 4: Get Webhook Secret
1. **Click** on your webhook endpoint
2. **Copy**: Signing secret (`whsec_...`)

---

## ⚙️ **3. ENVIRONMENT CONFIGURATION**

### Step 1: Create Environment File
Create `.env` file in project root:

```bash
# Create .env file
touch .env
```

### Step 2: Add Stripe Configuration
```env
# .env file content
DEBUG=True
SECRET_KEY=your-django-secret-key

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Database Configuration
DB_NAME=accorix_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 3: Update Django Settings
The system is already configured to read from environment variables.

### Step 4: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify Stripe installation
python -c "import stripe; print(f'Stripe version: {stripe.__version__}')"
```

---

## 🧪 **4. TESTING THE INTEGRATION**

### Step 1: Start Development Server
```bash
# Run migrations
python manage.py migrate

# Create superuser (if not exists)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Step 2: Test Payment Flow
1. **Login** as admin: http://127.0.0.1:8000/admin/
2. **Create** a customer invoice
3. **Access** portal as customer
4. **Initiate** payment with test card

### Step 3: Use Stripe Test Cards
```
# Successful Payment
Card: 4242 4242 4242 4242
Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits

# Declined Payment
Card: 4000 0000 0000 0002
Expiry: Any future date
CVC: Any 3 digits

# Requires Authentication
Card: 4000 0025 0000 3155
Expiry: Any future date
CVC: Any 3 digits
```

### Step 4: Test Webhook Locally
```bash
# Install Stripe CLI
# Download from: https://stripe.com/docs/stripe-cli

# Login to Stripe CLI
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/payments/webhook/

# Test webhook
stripe trigger payment_intent.succeeded
```

### Step 5: Verify Payment Records
1. **Check** Django admin: Payments → Stripe Payments
2. **Verify** invoice payment status updated
3. **Check** webhook logs in Stripe dashboard

---

## 🚀 **5. PRODUCTION DEPLOYMENT**

### Step 1: Get Production Keys
1. **Activate** your Stripe account (complete business verification)
2. **Switch** to Live mode in Stripe dashboard
3. **Get** production API keys:
   ```
   Publishable Key: pk_live_...
   Secret Key: sk_live_...
   ```

### Step 2: Update Production Environment
```env
# Production .env
DEBUG=False
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret
```

### Step 3: Configure Production Webhook
1. **Add** production webhook endpoint
2. **URL**: `https://yourdomain.com/payments/webhook/`
3. **SSL**: Ensure HTTPS is working
4. **Test**: Use Stripe dashboard webhook tester

### Step 4: Security Checklist
- ✅ HTTPS enabled
- ✅ Environment variables secured
- ✅ Database backups configured
- ✅ Error logging enabled
- ✅ Rate limiting implemented

---

## 🔧 **6. TROUBLESHOOTING**

### Common Issues & Solutions

#### Issue 1: "Invalid API Key"
```bash
# Check environment variables
python manage.py shell
>>> import os
>>> print(os.getenv('STRIPE_SECRET_KEY'))
```
**Solution**: Verify `.env` file and restart server

#### Issue 2: Webhook Signature Verification Failed
```python
# Check webhook secret
STRIPE_WEBHOOK_SECRET=whsec_correct_secret_here
```
**Solution**: Copy exact webhook secret from Stripe dashboard

#### Issue 3: Payment Intent Creation Failed
```python
# Check currency and amount
amount_in_cents = int(amount * 100)  # Convert to paise for INR
currency = 'inr'
```
**Solution**: Ensure amount is in smallest currency unit (paise)

#### Issue 4: CORS Issues in Production
```python
# Add to settings.py
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

### Debug Commands
```bash
# Check Stripe connectivity
python manage.py shell -c "import stripe; stripe.api_key='sk_test_...'; print(stripe.Account.retrieve())"

# Test webhook endpoint
curl -X POST http://localhost:8000/payments/webhook/ -H "Content-Type: application/json" -d '{}'

# Check payment records
python manage.py shell -c "from payments.models import StripePayment; print(StripePayment.objects.count())"
```

---

## 📊 **INTEGRATION STATUS**

### ✅ **Already Implemented**
- Stripe payment model and views
- Webhook handling for payment events
- Payment intent creation and processing
- Invoice payment linking
- Portal payment interface
- Admin dashboard for payment tracking

### 🔄 **Configuration Needed**
1. Add your Stripe API keys to `.env`
2. Configure webhook endpoint in Stripe dashboard
3. Test with Stripe test cards
4. Deploy with HTTPS for production

### 📈 **Features Available**
- **Multi-currency support** (INR optimized)
- **Automatic invoice payment linking**
- **Real-time payment status updates**
- **Comprehensive webhook handling**
- **Payment failure management**
- **Refund processing capability**

---

## 🎯 **NEXT STEPS**

1. **Get Stripe Account**: Sign up and verify business
2. **Add API Keys**: Update `.env` file with your keys
3. **Test Payments**: Use test cards to verify flow
4. **Configure Webhooks**: Set up webhook endpoint
5. **Go Live**: Switch to production keys when ready

**Need Help?** Check the troubleshooting section or Stripe documentation at https://stripe.com/docs