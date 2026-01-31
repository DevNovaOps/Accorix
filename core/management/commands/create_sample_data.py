from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.models import User, Contact, Product, AnalyticalAccount
from transactions.models import CustomerInvoice, VendorBill, SalesOrder, PurchaseOrder, CustomerInvoiceItem, VendorBillItem, SalesOrderItem, PurchaseOrderItem


class Command(BaseCommand):
    help = 'Create sample data for testing portal functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        try:
            with transaction.atomic():
                # Create sample products
                products = self.create_products(dry_run)
                
                # Create sample contacts
                contacts = self.create_contacts(dry_run)
                
                # Create sample users linked to contacts
                users = self.create_portal_users(contacts, dry_run)
                
                # Create sample invoices, bills, and orders
                self.create_sample_transactions(contacts, products, dry_run)
                
                if dry_run:
                    raise Exception("Dry run - rolling back changes")
                    
        except Exception as e:
            if not dry_run:
                self.stdout.write(self.style.ERROR(f'Error creating sample data: {str(e)}'))
            else:
                self.stdout.write(self.style.SUCCESS('Sample data creation completed (dry run)'))

    def create_products(self, dry_run):
        products_data = [
            {'name': 'Web Development Service', 'sku': 'WEB001', 'category': 'Services', 'unit_price': Decimal('150.00')},
            {'name': 'Mobile App Development', 'sku': 'MOB001', 'category': 'Services', 'unit_price': Decimal('200.00')},
            {'name': 'Consulting Hours', 'sku': 'CON001', 'category': 'Services', 'unit_price': Decimal('120.00')},
            {'name': 'Software License', 'sku': 'LIC001', 'category': 'Software', 'unit_price': Decimal('500.00')},
            {'name': 'Hosting Service', 'sku': 'HOST001', 'category': 'Services', 'unit_price': Decimal('50.00')},
        ]
        
        products = []
        for product_data in products_data:
            if not dry_run:
                product, created = Product.objects.get_or_create(
                    sku=product_data['sku'],
                    defaults=product_data
                )
                products.append(product)
                if created:
                    self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'[DRY RUN] Would create product: {product_data["name"]}')
                
        return products

    def create_contacts(self, dry_run):
        contacts_data = [
            {'name': 'Acme Corporation', 'email': 'customer1@acme.com', 'contact_type': 'customer', 'phone': '555-0101'},
            {'name': 'Tech Solutions Inc', 'email': 'customer2@techsol.com', 'contact_type': 'customer', 'phone': '555-0102'},
            {'name': 'Global Services Ltd', 'email': 'vendor1@global.com', 'contact_type': 'vendor', 'phone': '555-0201'},
            {'name': 'Supply Chain Co', 'email': 'vendor2@supply.com', 'contact_type': 'vendor', 'phone': '555-0202'},
        ]
        
        contacts = []
        for contact_data in contacts_data:
            if not dry_run:
                contact, created = Contact.objects.get_or_create(
                    email=contact_data['email'],
                    defaults=contact_data
                )
                contacts.append(contact)
                if created:
                    self.stdout.write(f'Created contact: {contact.name} ({contact.contact_type})')
            else:
                self.stdout.write(f'[DRY RUN] Would create contact: {contact_data["name"]} ({contact_data["contact_type"]})')
                
        return contacts

    def create_portal_users(self, contacts, dry_run):
        users = []
        for contact in contacts:
            username = contact.email.split('@')[0]
            
            if not dry_run:
                user, created = User.objects.get_or_create(
                    email=contact.email,
                    defaults={
                        'username': username,
                        'login_id': username,
                        'first_name': contact.name.split()[0],
                        'last_name': contact.name.split()[-1] if len(contact.name.split()) > 1 else '',
                        'role': contact.contact_type,
                        'contact': contact,
                    }
                )
                if created:
                    user.set_password('password123')  # Default password
                    user.save()
                    users.append(user)
                    self.stdout.write(f'Created user: {user.username} (role: {user.role})')
            else:
                self.stdout.write(f'[DRY RUN] Would create user: {username} (role: {contact.contact_type})')
                
        return users

    def create_sample_transactions(self, contacts, products, dry_run):
        if dry_run:
            self.stdout.write('[DRY RUN] Would create sample invoices, bills, and orders')
            return
            
        # Get admin user for created_by field
        admin_user = User.objects.filter(role='admin').first()
        if not admin_user:
            admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            self.stdout.write(self.style.WARNING('No admin user found, skipping transaction creation'))
            return

        # Create sample invoices for customers
        customers = [c for c in contacts if c.contact_type == 'customer']
        for i, customer in enumerate(customers):
            # Create 3 invoices per customer
            for j in range(3):
                invoice = CustomerInvoice.objects.create(
                    transaction_number=f'INV-{customer.id:03d}-{j+1:03d}',
                    contact=customer,
                    date=timezone.now().date() - timedelta(days=30-j*10),
                    due_date=timezone.now().date() - timedelta(days=30-j*10) + timedelta(days=30),
                    status='posted',
                    payment_status='not_paid' if j == 0 else ('partially_paid' if j == 1 else 'paid'),
                    created_by=admin_user,
                )
                
                # Add items to invoice
                for k, product in enumerate(products[:2]):
                    CustomerInvoiceItem.objects.create(
                        customer_invoice=invoice,
                        product=product,
                        quantity=k+1,
                        unit_price=product.unit_price,
                    )
                
                self.stdout.write(f'Created invoice: {invoice.transaction_number}')

        # Create sample bills for vendors
        vendors = [c for c in contacts if c.contact_type == 'vendor']
        for i, vendor in enumerate(vendors):
            # Create 2 bills per vendor
            for j in range(2):
                bill = VendorBill.objects.create(
                    transaction_number=f'BILL-{vendor.id:03d}-{j+1:03d}',
                    contact=vendor,
                    date=timezone.now().date() - timedelta(days=20-j*10),
                    due_date=timezone.now().date() - timedelta(days=20-j*10) + timedelta(days=30),
                    status='posted',
                    payment_status='not_paid' if j == 0 else 'paid',
                    created_by=admin_user,
                )
                
                # Add items to bill
                for k, product in enumerate(products[2:4]):
                    VendorBillItem.objects.create(
                        vendor_bill=bill,
                        product=product,
                        quantity=k+1,
                        unit_price=product.unit_price,
                    )
                
                self.stdout.write(f'Created bill: {bill.transaction_number}')

        # Create sample sales orders for customers
        for i, customer in enumerate(customers):
            order = SalesOrder.objects.create(
                transaction_number=f'SO-{customer.id:03d}-001',
                contact=customer,
                date=timezone.now().date() - timedelta(days=5),
                status='posted',
                created_by=admin_user,
            )
            
            # Add items to order
            SalesOrderItem.objects.create(
                sales_order=order,
                product=products[0],
                quantity=2,
                unit_price=products[0].unit_price,
            )
            
            self.stdout.write(f'Created sales order: {order.transaction_number}')

        # Create sample purchase orders for vendors
        for i, vendor in enumerate(vendors):
            order = PurchaseOrder.objects.create(
                transaction_number=f'PO-{vendor.id:03d}-001',
                contact=vendor,
                date=timezone.now().date() - timedelta(days=3),
                status='posted',
                created_by=admin_user,
            )
            
            # Add items to order
            PurchaseOrderItem.objects.create(
                purchase_order=order,
                product=products[2],
                quantity=1,
                unit_price=products[2].unit_price,
            )
            
            self.stdout.write(f'Created purchase order: {order.transaction_number}')

        self.stdout.write(self.style.SUCCESS('Sample transactions created successfully!'))