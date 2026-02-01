#!/usr/bin/env python
"""
Complete System Setup Script for ACCORIX
This script sets up the entire accounting system with sample data
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accorix.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Contact, Product, AnalyticalAccount, AutoAnalyticalModel
from transactions.models import (
    ChartOfAccounts, CustomerInvoice, CustomerInvoiceItem, 
    VendorBill, VendorBillItem, SalesOrder, SalesOrderItem,
    PurchaseOrder, PurchaseOrderItem, Payment
)
from budgets.models import Budget, BudgetStageMapping, BudgetFieldExplanation
from analytics.models import PDFDocument, AnalyticsReport
from payments.models import StripePayment

User = get_user_model()

def create_users():
    """Create sample users"""
    print("Creating users...")
    
    # Admin user
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'login_id': 'admin123',
            'email': 'admin@accorix.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"✓ Created admin user: {admin.username}")
    
    # Invoicing user
    invoicing, created = User.objects.get_or_create(
        username='invoicing',
        defaults={
            'login_id': 'invoice123',
            'email': 'invoicing@accorix.com',
            'first_name': 'Invoice',
            'last_name': 'Manager',
            'role': 'invoicing',
        }
    )
    if created:
        invoicing.set_password('invoice123')
        invoicing.save()
        print(f"✓ Created invoicing user: {invoicing.username}")
    
    return admin, invoicing

def create_chart_of_accounts():
    """Create chart of accounts"""
    print("Creating chart of accounts...")
    
    accounts_data = [
        # Assets
        ('1000', 'Cash and Cash Equivalents', 'assets', None),
        ('1100', 'Bank Account - Main', 'assets', None),
        ('1200', 'Accounts Receivable', 'assets', None),
        ('1300', 'Inventory', 'assets', None),
        ('1400', 'Equipment', 'assets', None),
        
        # Liabilities
        ('2000', 'Accounts Payable', 'liabilities', None),
        ('2100', 'Accrued Expenses', 'liabilities', None),
        ('2200', 'Short-term Loans', 'liabilities', None),
        
        # Equity
        ('3000', 'Owner\'s Capital', 'equity', None),
        ('3100', 'Retained Earnings', 'equity', None),
        
        # Income
        ('4000', 'Sales Revenue', 'income', None),
        ('4100', 'Service Income', 'income', None),
        ('4200', 'Other Income', 'income', None),
        
        # Expenses
        ('5000', 'Cost of Goods Sold', 'expense', None),
        ('5100', 'Office Rent', 'expense', None),
        ('5200', 'Utilities', 'expense', None),
        ('5300', 'Marketing Expenses', 'expense', None),
        ('5400', 'Travel Expenses', 'expense', None),
        ('5500', 'Professional Services', 'expense', None),
    ]
    
    for code, name, acc_type, parent in accounts_data:
        account, created = ChartOfAccounts.objects.get_or_create(
            account_code=code,
            defaults={
                'account_name': name,
                'account_type': acc_type,
                'parent_account': parent,
                'status': 'confirmed',
            }
        )
        if created:
            print(f"✓ Created account: {code} - {name}")

def create_contacts():
    """Create sample contacts"""
    print("Creating contacts...")
    
    customers_data = [
        ('Acme Corporation', 'acme@example.com', '+91-9876543210', 'customer'),
        ('Tech Solutions Ltd', 'tech@solutions.com', '+91-9876543211', 'customer'),
        ('Global Enterprises', 'global@enterprises.com', '+91-9876543212', 'customer'),
        ('Digital Innovations', 'digital@innovations.com', '+91-9876543213', 'customer'),
        ('Future Systems', 'future@systems.com', '+91-9876543214', 'customer'),
    ]
    
    vendors_data = [
        ('Office Supplies Co', 'office@supplies.com', '+91-9876543220', 'vendor'),
        ('Tech Equipment Ltd', 'tech@equipment.com', '+91-9876543221', 'vendor'),
        ('Professional Services', 'professional@services.com', '+91-9876543222', 'vendor'),
        ('Utility Company', 'utility@company.com', '+91-9876543223', 'vendor'),
        ('Marketing Agency', 'marketing@agency.com', '+91-9876543224', 'vendor'),
    ]
    
    contacts = []
    
    for name, email, phone, contact_type in customers_data + vendors_data:
        contact, created = Contact.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'phone': phone,
                'contact_type': contact_type,
                'status': 'confirmed',
                'address': f'123 Business Street, City, State - 12345',
            }
        )
        if created:
            print(f"✓ Created {contact_type}: {name}")
        contacts.append(contact)
    
    # Create portal users for some contacts
    portal_contacts = contacts[:3]  # First 3 contacts
    for i, contact in enumerate(portal_contacts):
        portal_user, created = User.objects.get_or_create(
            username=f'portal_user_{i+1}',
            defaults={
                'login_id': f'portal{i+1:03d}',
                'email': contact.email,
                'first_name': contact.name.split()[0],
                'last_name': ' '.join(contact.name.split()[1:]) if len(contact.name.split()) > 1 else '',
                'role': contact.contact_type,
                'contact': contact,
            }
        )
        if created:
            portal_user.set_password('portal123')
            portal_user.save()
            print(f"✓ Created portal user: {portal_user.username} for {contact.name}")
    
    return contacts

def create_products():
    """Create sample products"""
    print("Creating products...")
    
    products_data = [
        ('Software License', 'SOFT-001', 'Annual software license', 'Software', 50000, 55000, 45000),
        ('Consulting Hours', 'CONS-001', 'Professional consulting services', 'Services', 2500, 3000, 2000),
        ('Training Program', 'TRAIN-001', 'Employee training program', 'Training', 15000, 18000, 12000),
        ('Hardware Setup', 'HARD-001', 'Computer hardware setup', 'Hardware', 25000, 30000, 20000),
        ('Maintenance Contract', 'MAINT-001', 'Annual maintenance contract', 'Services', 12000, 15000, 10000),
        ('Office Chair', 'CHAIR-001', 'Ergonomic office chair', 'Furniture', 8000, 10000, 6000),
        ('Laptop Computer', 'LAPTOP-001', 'Business laptop computer', 'Electronics', 45000, 50000, 40000),
        ('Printer', 'PRINT-001', 'Laser printer', 'Electronics', 15000, 18000, 12000),
    ]
    
    products = []
    for name, sku, desc, category, unit_price, sale_price, purchase_price in products_data:
        product, created = Product.objects.get_or_create(
            sku=sku,
            defaults={
                'name': name,
                'description': desc,
                'category': category,
                'unit_price': Decimal(str(unit_price)),
                'sale_price': Decimal(str(sale_price)),
                'purchase_price': Decimal(str(purchase_price)),
                'status': 'confirmed',
            }
        )
        if created:
            print(f"✓ Created product: {name}")
        products.append(product)
    
    return products

def create_analytical_accounts():
    """Create analytical accounts (cost centers)"""
    print("Creating analytical accounts...")
    
    accounts_data = [
        ('CC-001', 'Sales Department', 'Sales team expenses and activities'),
        ('CC-002', 'Marketing Department', 'Marketing campaigns and promotions'),
        ('CC-003', 'IT Department', 'Technology infrastructure and support'),
        ('CC-004', 'HR Department', 'Human resources and recruitment'),
        ('CC-005', 'Operations', 'General business operations'),
        ('CC-006', 'Research & Development', 'Product development and innovation'),
    ]
    
    analytical_accounts = []
    for code, name, desc in accounts_data:
        account, created = AnalyticalAccount.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': desc,
                'status': 'confirmed',
            }
        )
        if created:
            print(f"✓ Created analytical account: {code} - {name}")
        analytical_accounts.append(account)
    
    return analytical_accounts

def create_budgets(analytical_accounts):
    """Create sample budgets"""
    print("Creating budgets...")
    
    current_year = date.today().year
    start_date = date(current_year, 1, 1)
    end_date = date(current_year, 12, 31)
    
    for account in analytical_accounts:
        budget_amount = random.randint(100000, 500000)
        budget, created = Budget.objects.get_or_create(
            name=f'{account.name} Budget {current_year}',
            analytical_account=account,
            start_date=start_date,
            end_date=end_date,
            defaults={
                'budgeted_amount': Decimal(str(budget_amount)),
                'status': 'confirmed',
                'stage': 'active',
            }
        )
        if created:
            print(f"✓ Created budget: {budget.name} - ₹{budget_amount:,}")

def create_transactions(contacts, products, analytical_accounts, admin_user):
    """Create sample transactions"""
    print("Creating sample transactions...")
    
    customers = [c for c in contacts if c.contact_type in ['customer', 'both']]
    vendors = [c for c in contacts if c.contact_type in ['vendor', 'both']]
    
    # Create Customer Invoices
    for i in range(10):
        customer = random.choice(customers)
        analytical_account = random.choice(analytical_accounts)
        
        invoice_date = date.today() - timedelta(days=random.randint(1, 90))
        due_date = invoice_date + timedelta(days=30)
        
        invoice = CustomerInvoice.objects.create(
            date=invoice_date,
            due_date=due_date,
            contact=customer,
            analytical_account=analytical_account,
            invoice_number=f'INV-{i+1:04d}',
            status='posted',
            payment_status=random.choice(['not_paid', 'partially_paid', 'paid']),
            created_by=admin_user,
        )
        
        # Add invoice items
        num_items = random.randint(1, 3)
        for j in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            unit_price = product.sale_price or product.unit_price
            
            CustomerInvoiceItem.objects.create(
                customer_invoice=invoice,
                product=product,
                quantity=Decimal(str(quantity)),
                unit_price=unit_price,
                analytical_account=analytical_account,
            )
        
        print(f"✓ Created invoice: {invoice.transaction_number}")
    
    # Create Vendor Bills
    for i in range(8):
        vendor = random.choice(vendors)
        analytical_account = random.choice(analytical_accounts)
        
        bill_date = date.today() - timedelta(days=random.randint(1, 60))
        due_date = bill_date + timedelta(days=30)
        
        bill = VendorBill.objects.create(
            date=bill_date,
            due_date=due_date,
            contact=vendor,
            analytical_account=analytical_account,
            bill_number=f'BILL-{i+1:04d}',
            status='posted',
            payment_status=random.choice(['not_paid', 'partially_paid', 'paid']),
            created_by=admin_user,
        )
        
        # Add bill items
        num_items = random.randint(1, 2)
        for j in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 3)
            unit_price = product.purchase_price or product.unit_price
            
            VendorBillItem.objects.create(
                vendor_bill=bill,
                product=product,
                quantity=Decimal(str(quantity)),
                unit_price=unit_price,
                analytical_account=analytical_account,
            )
        
        print(f"✓ Created vendor bill: {bill.transaction_number}")

def create_budget_configurations():
    """Create budget configuration data"""
    print("Creating budget configurations...")
    
    # Budget Stage Mappings
    stages_data = [
        ('planning', 'Planning Phase', '#6B7280', 1),
        ('approved', 'Approved', '#10B981', 2),
        ('active', 'Active', '#3B82F6', 3),
        ('monitoring', 'Under Monitoring', '#F59E0B', 4),
        ('closed', 'Closed', '#6B7280', 5),
    ]
    
    for stage, description, color, order in stages_data:
        mapping, created = BudgetStageMapping.objects.get_or_create(
            stage=stage,
            defaults={
                'description': description,
                'color_code': color,
                'order': order,
            }
        )
        if created:
            print(f"✓ Created budget stage: {stage}")
    
    # Budget Field Explanations
    explanations_data = [
        ('budgeted_amount', 'Budgeted Amount', 'The total amount allocated for this budget period', 'Example: ₹100,000 for marketing expenses'),
        ('analytical_account', 'Analytical Account', 'The cost center or department this budget applies to', 'Example: Marketing Department, IT Department'),
        ('start_date', 'Start Date', 'The beginning date of the budget period', 'Example: 2024-01-01 for annual budget'),
        ('end_date', 'End Date', 'The ending date of the budget period', 'Example: 2024-12-31 for annual budget'),
        ('status', 'Budget Status', 'Current approval status of the budget', 'Draft, Confirmed, or Archived'),
    ]
    
    for field, title, explanation, example in explanations_data:
        exp, created = BudgetFieldExplanation.objects.get_or_create(
            field_name=field,
            defaults={
                'title': title,
                'explanation': explanation,
                'example': example,
            }
        )
        if created:
            print(f"✓ Created field explanation: {field}")

def main():
    """Main setup function"""
    print("🚀 Starting ACCORIX Complete System Setup...")
    print("=" * 50)
    
    try:
        # Create users
        admin_user, invoicing_user = create_users()
        
        # Create chart of accounts
        create_chart_of_accounts()
        
        # Create contacts
        contacts = create_contacts()
        
        # Create products
        products = create_products()
        
        # Create analytical accounts
        analytical_accounts = create_analytical_accounts()
        
        # Create budgets
        create_budgets(analytical_accounts)
        
        # Create transactions
        create_transactions(contacts, products, analytical_accounts, admin_user)
        
        # Create budget configurations
        create_budget_configurations()
        
        print("=" * 50)
        print("✅ ACCORIX System Setup Complete!")
        print("\n📋 Login Credentials:")
        print("Admin User:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  URL: http://localhost:8000/login/")
        print("\nInvoicing User:")
        print("  Username: invoicing")
        print("  Password: invoice123")
        print("\nPortal Users:")
        print("  Username: portal_user_1, portal_user_2, portal_user_3")
        print("  Password: portal123")
        print("  URL: http://localhost:8000/portal/")
        print("\n🎯 Features Available:")
        print("  • Complete Chart of Accounts")
        print("  • Customer & Vendor Management")
        print("  • Product Catalog")
        print("  • Invoice & Bill Management with PDF Generation")
        print("  • Budget Planning & Monitoring")
        print("  • Analytics Dashboard with Charts")
        print("  • Stripe Payment Integration")
        print("  • PDF Document Processing & Generation")
        print("  • Portal for Customers & Vendors with PDF Downloads")
        print("  • Professional PDF Invoices & Bills")
        print("\n📄 PDF Features:")
        print("  • Generate professional PDF invoices")
        print("  • Generate professional PDF bills")
        print("  • Download PDFs from admin interface")
        print("  • Download PDFs from portal interface")
        print("  • Branded PDF templates with company logo")
        print("  • Detailed line items and payment information")
        print("\n🚀 Start the server with: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()