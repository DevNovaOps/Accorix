# ACCORIX Finance OS

A comprehensive ERP financial management system built with Django, MySQL, HTML, CSS, and JavaScript.

## Features

### User Management
- **Login/Signup**: Secure authentication with validation
- **Role-based Access**: Admin, Portal User, and Invoicing User roles
- **User Creation**: Admin can create users with different roles

### Master Data Management
- **Contacts**: Manage customers and vendors
- **Products**: Product catalog with SKU, pricing, and categories
- **Analytical Accounts**: Cost centers for budget tracking
- **Auto Analytical Models**: Automated rules for linking transactions to cost centers

### Transaction Processing
- **Purchase Orders**: Track purchase orders from vendors
- **Vendor Bills**: Record and manage vendor bills
- **Sales Orders**: Manage customer sales orders
- **Customer Invoices**: Generate and track customer invoices
- **Payments**: Record payments with automatic status updates

### Budget Monitoring
- **Budget vs Actual**: Real-time comparison of budgeted vs actual spending
- **Achievement Percentage**: Track budget utilization
- **Remaining Balance**: Monitor remaining budget
- **Budget Revisions**: Track changes to budgets over time
- **Dashboard**: Visual dashboard with charts and reports

### Customer Portal
- **Invoice/Bill Viewing**: Customers can view their invoices and bills
- **Order Tracking**: View purchase orders and sales orders
- **Document Download**: Download invoices and bills
- **Online Payments**: Make payments directly from the portal

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: MySQL
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Icons**: Phosphor Icons

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Acc
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL Database**
   - Create a MySQL database named `accorix_db`
   - Update database settings in `accorix/settings.py` or use environment variables

5. **Set up environment variables** (optional)
   Create a `.env` file:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=accorix_db
   DB_USER=root
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=3306
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser** (Admin user)
   ```bash
   python manage.py createsuperuser
   ```
   Note: You'll need to set the `login_id` field manually in the admin or use Django shell.

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - Login with your admin credentials

## User Roles

### Admin
- Full access to all features
- Can create, edit, and archive master data
- Can create users
- Can view all reports and transactions

### Invoicing User
- Can create transactions (PO, SO, Invoices, Bills)
- Can view master data
- Cannot modify or archive master data

### Portal User
- Can view their own invoices, bills, and orders
- Can download documents
- Can make online payments
- Limited to their own data only

## Validation Rules

### Login ID
- Must be between 6-12 characters
- Must be unique

### Email
- Must be unique in the database

### Password
- Minimum 8 characters
- Must contain at least one lowercase letter
- Must contain at least one uppercase letter
- Must contain at least one special character

## Key Concepts

### Analytical Accounts (Cost Centers)
Track *where* or on *what activity* money is being spent, as opposed to Chart of Accounts which tracks *what* the money is for.

### Budget vs Actuals
Compare planned financial targets (Budget) against real-world transactions (Actuals). Actuals are pulled from "Posted" journal entries.

### Auto-Analytical Models
Automated rules that link transactions to analytical accounts based on conditions like product category, product name, or contact type.

### Payment Status
- **Fully Paid**: Payment amount equals the Invoice/Bill total
- **Partially Paid**: A payment was made, but a balance remains
- **Not Paid**: No payments recorded

## Development

### Project Structure
```
Acc/
├── accorix/          # Main Django project
├── core/             # Core app (Users, Master Data)
├── transactions/     # Transaction processing
├── budgets/          # Budget management
├── portal/           # Customer portal
├── templates/        # HTML templates
├── static/           # Static files
└── manage.py
```

## License

This project is created for hackathon purposes.
