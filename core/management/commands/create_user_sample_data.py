from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.models import User, Contact, Product
from transactions.models import CustomerInvoice, VendorBill, SalesOrder, PurchaseOrder, CustomerInvoiceItem, VendorBillItem, SalesOrderItem, PurchaseOrderItem


class Command(BaseCommand):
    help = 'Create sample data for existing portal users'

    def handle(self, *args, **options):
        self.stdout.write("📊 Creating Sample Data for Existing Portal Users...")
        self.stdout.write("=" * 60)
        
        try:
            with transaction.atomic():
                # Get admin user for created_by field
                admin_user = User.objects.filter(role='admin').first()
                if not admin_user:
                    self.stdout.write(self.style.ERROR('No admin user found'))
                    return
                
                # Get products
                products = list(Product.objects.all()[:5])
                if not products:
                    self.stdout.write(self.style.ERROR('No products found. Run create_sample_data first.'))
                    return
                
                # Create sample data for existing customer users
                customer_users = User.objects.filter(role='customer', contact__isnull=False)
                for user in customer_users:
                    if user.contact:
                        self.create_customer_data(user.contact, products, admin_user)
                
                # Create sample data for existing vendor users  
                vendor_users = User.objects.filter(role='vendor', contact__isnull=False)
                for user in vendor_users:
                    if user.contact:
                        self.create_vendor_data(user.contact, products, admin_user)
                
                self.stdout.write(self.style.SUCCESS('\n🎉 Sample data created for existing portal users!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating sample data: {str(e)}'))
    
    def create_customer_data(self, contact, products, admin_user):
        self.stdout.write(f"\n👤 Creating data for customer: {contact.name}")
        
        # Create 2-3 invoices
        for i in range(3):
            invoice = CustomerInvoice.objects.create(
                transaction_number=f'INV-USER-{contact.id:03d}-{i+1:03d}',
                contact=contact,
                date=timezone.now().date() - timedelta(days=45-i*15),
                due_date=timezone.now().date() - timedelta(days=45-i*15) + timedelta(days=30),
                status='posted',
                payment_status='not_paid' if i == 0 else ('partially_paid' if i == 1 else 'paid'),
                created_by=admin_user,
            )
            
            # Add 1-2 items to each invoice
            for j in range(2):
                if j < len(products):
                    CustomerInvoiceItem.objects.create(
                        customer_invoice=invoice,
                        product=products[j],
                        quantity=j+1,
                        unit_price=products[j].unit_price,
                    )
            
            self.stdout.write(f"   📄 Created invoice: {invoice.transaction_number} (${invoice.total_amount})")
        
        # Create 1-2 sales orders
        for i in range(2):
            order = SalesOrder.objects.create(
                transaction_number=f'SO-USER-{contact.id:03d}-{i+1:03d}',
                contact=contact,
                date=timezone.now().date() - timedelta(days=10-i*5),
                status='posted',
                created_by=admin_user,
            )
            
            # Add item to order
            if products:
                SalesOrderItem.objects.create(
                    sales_order=order,
                    product=products[0],
                    quantity=i+1,
                    unit_price=products[0].unit_price,
                )
            
            self.stdout.write(f"   📦 Created sales order: {order.transaction_number} (${order.total_amount})")
    
    def create_vendor_data(self, contact, products, admin_user):
        self.stdout.write(f"\n🏢 Creating data for vendor: {contact.name}")
        
        # Create 2 bills
        for i in range(2):
            bill = VendorBill.objects.create(
                transaction_number=f'BILL-USER-{contact.id:03d}-{i+1:03d}',
                contact=contact,
                date=timezone.now().date() - timedelta(days=30-i*15),
                due_date=timezone.now().date() - timedelta(days=30-i*15) + timedelta(days=30),
                status='posted',
                payment_status='not_paid' if i == 0 else 'paid',
                created_by=admin_user,
            )
            
            # Add 1-2 items to each bill
            for j in range(2):
                if j+2 < len(products):
                    VendorBillItem.objects.create(
                        vendor_bill=bill,
                        product=products[j+2],  # Use different products for bills
                        quantity=j+1,
                        unit_price=products[j+2].unit_price,
                    )
            
            self.stdout.write(f"   📄 Created bill: {bill.transaction_number} (${bill.total_amount})")
        
        # Create 1 purchase order
        order = PurchaseOrder.objects.create(
            transaction_number=f'PO-USER-{contact.id:03d}-001',
            contact=contact,
            date=timezone.now().date() - timedelta(days=7),
            status='posted',
            created_by=admin_user,
        )
        
        # Add item to order
        if len(products) > 2:
            PurchaseOrderItem.objects.create(
                purchase_order=order,
                product=products[2],
                quantity=1,
                unit_price=products[2].unit_price,
            )
        
        self.stdout.write(f"   📦 Created purchase order: {order.transaction_number} (${order.total_amount})")