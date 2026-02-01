# 🚀 **ACCORIX ERP - QUICK START GUIDE**

## 📋 **Overview**
ACCORIX is a complete ERP system with accounting, budgeting, analytics, and Stripe payment integration. This guide will get you up and running in minutes.

---

## ⚡ **Quick Setup (5 Minutes)**

### 1. **Clone & Install**
```bash
# Clone the repository
git clone https://github.com/yourusername/accorix-erp.git
cd accorix-erp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Database Setup**
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE accorix_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Run migrations
python manage.py migrate
```

### 3. **Initial Configuration**
```bash
# Run setup script (creates .env, superuser, basic data)
python setup_production.py

# Or manual setup:
python manage.py createsuperuser
python setup_complete_system.py
```

### 4. **Start Development Server**
```bash
python manage.py runserver
```

### 5. **Access the System**
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Main Dashboard**: http://127.0.0.1:8000/
- **Analytics**: http://127.0.0.1:8000/analytics/

---

## 💳 **Stripe Integration (2 Minutes)**

### 1. **Get Stripe Account**
- Sign up at https://dashboard.stripe.com/register
- Get your API keys from Developers → API Keys

### 2. **Configure Environment**
Update your `.env` file:
```env
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 3. **Test Payment**
- Create a customer invoice
- Use test card: `4242 4242 4242 4242`
- Process payment through portal

---

## 🎯 **Key Features**

### ✅ **What's Already Working**
- **User Management**: Role-based access (Admin, Invoicing, Portal)
- **Financial Transactions**: Invoices, Bills, Orders, Payments
- **Budget Management**: Real-time budget tracking with overrides
- **Analytics Dashboard**: Interactive charts with Matplotlib
- **PDF Generation**: Professional invoices and bills
- **Stripe Payments**: Complete payment gateway integration
- **Portal Access**: Customer and vendor self-service portals

### 🔧 **Payment Methods Available**
- **Bank Transfer**: Direct bank transfers
- **Credit Card**: Credit card payments
- **Online Payment**: General online payments
- **Stripe Payment**: Stripe gateway integration

### 📊 **Analytics Features**
- Revenue vs Expense charts
- Monthly financial trends
- Top customers analysis
- Budget variance tracking
- Custom report generation

---

## 📁 **System Structure**

```
accorix/
├── 🏢 Core Modules
│   ├── core/              # Users, contacts, products
│   ├── transactions/      # Invoices, bills, payments
│   ├── budgets/          # Budget management
│   ├── analytics/        # Reports and charts
│   ├── payments/         # Stripe integration
│   └── portal/           # Customer/vendor access
│
├── 🎨 Frontend
│   ├── templates/        # Dark theme UI
│   └── static/          # CSS, JS, images
│
└── 📋 Documentation
    ├── STRIPE_INTEGRATION_GUIDE.md
    ├── DEPLOYMENT_CHECKLIST.md
    └── SYSTEM_ARCHITECTURE.md
```

---

## 🔐 **Default Login Credentials**

After running setup, use the superuser credentials you created, or:

**Admin User**:
- Username: admin
- Password: (set during setup)
- Role: Admin (full access)

**Test Portal Users**:
- Create customers/vendors in admin panel
- They can access portal with their credentials

---

## 🧪 **Testing the System**

### 1. **Create Test Data**
```bash
# Run the complete system setup
python setup_complete_system.py
```

### 2. **Test Core Features**
- ✅ Create a customer invoice
- ✅ Generate PDF
- ✅ Process payment via Stripe
- ✅ View analytics dashboard
- ✅ Test budget controls

### 3. **Test Stripe Integration**
Use these test cards:
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0025 0000 3155
```

---

## 🚨 **Troubleshooting**

### Common Issues:

**1. Database Connection Error**
```bash
# Check MySQL service
sudo systemctl status mysql
# Update .env with correct credentials
```

**2. Stripe Key Error**
```bash
# Verify keys in .env file
# Ensure keys start with pk_test_ and sk_test_
```

**3. PDF Generation Issues**
```bash
# Install ReportLab
pip install reportlab
# Check media directory permissions
```

**4. Analytics Charts Not Loading**
```bash
# Install matplotlib
pip install matplotlib
# Check if data exists in database
```

---

## 📞 **Support & Documentation**

- **Detailed Stripe Setup**: See `STRIPE_INTEGRATION_GUIDE.md`
- **Production Deployment**: See `DEPLOYMENT_CHECKLIST.md`
- **System Architecture**: See `SYSTEM_ARCHITECTURE.md`
- **Issues**: Create GitHub issue or contact support

---

## 🎉 **You're Ready!**

Your ACCORIX ERP system is now ready for use. The system includes:

- ✅ Complete accounting functionality
- ✅ Real-time budget management
- ✅ Professional PDF generation
- ✅ Stripe payment integration
- ✅ Analytics and reporting
- ✅ Customer/vendor portals

**Next Steps**:
1. Customize the system for your business
2. Add your actual Stripe keys for live payments
3. Configure email settings for notifications
4. Deploy to production when ready

**Happy accounting! 🎯**