# ACCORIX - Complete Accounting & ERP System

A comprehensive Django-based accounting and ERP system with advanced features including budget management, analytics, payment processing, and portal access for customers and vendors.

## 🌟 Features

### Core Accounting
- **Chart of Accounts** - Complete accounting structure with assets, liabilities, equity, income, and expenses
- **Customer & Vendor Management** - Comprehensive contact management with portal access
- **Product Catalog** - Product management with pricing and categorization
- **Invoice Management** - Customer invoices with payment tracking
- **Bill Management** - Vendor bills with approval workflows
- **Payment Processing** - Multiple payment methods including Stripe integration

### Advanced Features
- **Budget Planning & Monitoring** - Create budgets with real-time variance analysis
- **Analytical Accounts** - Cost center tracking and reporting
- **Analytics Dashboard** - Interactive charts using matplotlib
- **PDF Document Processing** - Upload and extract data from PDF documents
- **Portal Access** - Customer and vendor self-service portals
- **Multi-currency Support** - Indian Rupee (₹) with international support

### Technical Features
- **Dark/Light Theme** - Modern responsive UI with theme switching
- **Real-time Charts** - Revenue, expenses, budget variance, and trend analysis
- **Stripe Integration** - Secure online payments with webhook support
- **Role-based Access** - Admin, invoicing, customer, and vendor roles
- **Mobile Responsive** - Works on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+ or 8.0+
- Node.js (for frontend dependencies, optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd accorix
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Database Setup**
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE accorix_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Update database settings in accorix/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'accorix_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Setup complete system with sample data**
```bash
python setup_complete_system.py
```

7. **Start the development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Admin Panel: http://localhost:8000/admin/
- Main Application: http://localhost:8000/
- Portal: http://localhost:8000/portal/

## 👥 Default Users

### Admin User
- **Username:** admin
- **Password:** admin123
- **Role:** System Administrator
- **Access:** Full system access

### Invoicing User
- **Username:** invoicing
- **Password:** invoice123
- **Role:** Invoicing Manager
- **Access:** Transaction management

### Portal Users
- **Username:** portal_user_1, portal_user_2, portal_user_3
- **Password:** portal123
- **Role:** Customer/Vendor
- **Access:** Portal dashboard, invoices, payments

## 🔧 Configuration

### Stripe Payment Setup

1. **Get Stripe API Keys**
   - Sign up at https://stripe.com
   - Get your publishable and secret keys from the dashboard

2. **Update settings.py**
```python
STRIPE_PUBLISHABLE_KEY = 'pk_test_your_publishable_key_here'
STRIPE_SECRET_KEY = 'sk_test_your_secret_key_here'
STRIPE_WEBHOOK_SECRET = 'whsec_your_webhook_secret_here'
```

3. **Setup Webhook Endpoint**
   - In Stripe dashboard, add webhook endpoint: `https://yourdomain.com/payments/webhook/`
   - Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`, `charge.succeeded`

### Email Configuration (Optional)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 📊 System Architecture

### Apps Structure
```
accorix/
├── core/           # User management, contacts, products
├── transactions/   # Invoices, bills, payments, orders
├── budgets/        # Budget planning and monitoring
├── analytics/      # Charts, reports, PDF processing
├── payments/       # Stripe integration, payment processing
└── portal/         # Customer/vendor self-service portal
```

### Key Models
- **User** - Extended user model with roles
- **Contact** - Customers and vendors
- **Product** - Product catalog
- **CustomerInvoice/VendorBill** - Transaction documents
- **Budget** - Budget planning with analytical accounts
- **AnalyticalAccount** - Cost centers
- **ChartOfAccounts** - Accounting structure

## 🎨 UI Features

### Modern Design
- Dark theme with cyan/magenta accents
- Responsive grid layouts
- Interactive charts and graphs
- Mobile-first design

### Dashboard Features
- Real-time KPI cards
- Revenue vs expenses charts
- Monthly trend analysis
- Budget variance tracking
- Top customers analysis

### Portal Features
- Customer invoice viewing and payment
- Vendor bill management
- Order tracking
- Payment history
- Document downloads

## 📈 Analytics & Reporting

### Built-in Charts
- **Revenue vs Expenses** - Monthly comparison
- **Financial Trends** - Line charts with profit analysis
- **Top Customers** - Pie chart of revenue distribution
- **Budget Variance** - Actual vs budgeted spending

### PDF Processing
- Upload PDF documents
- Automatic text extraction
- Amount and date detection
- Document categorization

### Export Features
- CSV data export
- Custom report generation
- Chart image downloads

## 🔐 Security Features

- CSRF protection on all forms
- Role-based access control
- Secure payment processing
- File upload validation
- SQL injection prevention
- XSS protection

## 🛠️ Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

## 📱 API Endpoints

### Analytics
- `GET /analytics/` - Analytics dashboard
- `POST /analytics/pdf/upload/` - Upload PDF documents
- `GET /analytics/pdf/list/` - List documents

### Payments
- `POST /payments/create-payment-intent/` - Create Stripe payment
- `POST /payments/webhook/` - Stripe webhook handler
- `GET /payments/history/` - Payment history

### Transactions
- `GET /transactions/customer-invoices/` - Invoice list
- `POST /transactions/customer-invoices/create/` - Create invoice
- `GET /transactions/chart-of-accounts/` - Chart of accounts

## 🚀 Production Deployment

### Environment Variables
```bash
export DEBUG=False
export SECRET_KEY='your-secret-key'
export DATABASE_URL='mysql://user:pass@host:port/dbname'
export STRIPE_SECRET_KEY='sk_live_your_live_key'
```

### Static Files
```bash
python manage.py collectstatic --noinput
```

### Database
```bash
python manage.py migrate --noinput
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the setup script for examples

## 🔄 Updates

### Version 1.0.0
- Complete accounting system
- Stripe payment integration
- Analytics dashboard
- Portal access
- PDF processing
- Budget management

---

**ACCORIX** - Your Complete Accounting & ERP Solution 🚀
