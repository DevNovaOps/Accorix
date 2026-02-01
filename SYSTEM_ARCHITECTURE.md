# ACCORIX ERP - System Architecture

## 📁 Project Structure

```
accorix/
├── 🏢 Core System
│   ├── accorix/           # Main Django project
│   ├── core/              # User management, contacts, products
│   ├── transactions/      # Financial transactions (invoices, bills, orders)
│   ├── budgets/          # Budget management and tracking
│   ├── analytics/        # Reports and analytics with charts
│   ├── payments/         # Stripe payment integration
│   └── portal/           # Customer/vendor portal access
│
├── 🎨 Frontend
│   ├── templates/        # HTML templates with dark theme
│   ├── static/          # CSS, JS, images
│   └── media/           # Uploaded files and generated PDFs
│
├── 🔧 Configuration
│   ├── requirements.txt  # Python dependencies
│   ├── manage.py        # Django management
│   └── setup_*.py       # System initialization scripts
│
└── 📊 Features
    ├── PDF Generation    # Invoice/Bill PDFs with ReportLab
    ├── Chart Analytics   # Matplotlib integration
    ├── Budget Control    # Real-time budget validation
    └── Stripe Payments   # Complete payment gateway
```

## 🔄 Data Flow

```
User Input → Forms → Models → Database
     ↓
Business Logic → Validation → Budget Check
     ↓
PDF Generation ← Templates ← Views
     ↓
Analytics Dashboard ← Charts ← Data Processing
```

## 🛡️ Security Features

- Role-based access control (Admin, Invoicing, Portal users)
- Budget override protection with approval workflow
- Secure PDF generation with access validation
- Stripe webhook signature verification
- CSRF protection on all forms

## 🎯 Key Modules

### Core Module
- User management with roles
- Contact management (customers/vendors)
- Product catalog with categories
- Analytical accounts for cost centers

### Transactions Module
- Purchase Orders & Sales Orders
- Customer Invoices & Vendor Bills
- Payment processing with multiple methods
- Chart of Accounts for financial structure

### Analytics Module
- Real-time financial dashboards
- Custom report generation
- PDF document processing
- Interactive charts with Matplotlib

### Payments Module
- Stripe payment gateway integration
- Webhook handling for payment events
- Payment status tracking
- Multi-currency support (INR focus)

### Portal Module
- Customer self-service portal
- Vendor bill management
- Payment processing interface
- Document download access
```