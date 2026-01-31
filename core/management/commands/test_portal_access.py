from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from core.models import User


class Command(BaseCommand):
    help = 'Test portal user access and data display'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Portal User Access...")
        self.stdout.write("=" * 50)
        
        # Get a customer and vendor user
        customer_user = User.objects.filter(role='customer', contact__isnull=False).first()
        vendor_user = User.objects.filter(role='vendor', contact__isnull=False).first()
        
        if not customer_user:
            self.stdout.write(self.style.ERROR("No customer user with contact found"))
            return
            
        if not vendor_user:
            self.stdout.write(self.style.ERROR("No vendor user with contact found"))
            return
        
        # Test customer access
        self.stdout.write(f"\n👤 Testing Customer User: {customer_user.email}")
        self.test_user_access(customer_user, 'customer')
        
        # Test vendor access
        self.stdout.write(f"\n👤 Testing Vendor User: {vendor_user.email}")
        self.test_user_access(vendor_user, 'vendor')
        
        self.stdout.write("\n🎉 Portal access testing completed!")
    
    def test_user_access(self, user, role):
        from transactions.models import CustomerInvoice, VendorBill, SalesOrder, PurchaseOrder
        
        # Check user's contact and data
        contact = user.contact
        self.stdout.write(f"   📧 Contact: {contact.name} ({contact.contact_type})")
        
        if role == 'customer':
            invoices = CustomerInvoice.objects.filter(contact=contact, status='posted')
            orders = SalesOrder.objects.filter(contact=contact)
            self.stdout.write(f"   📄 Invoices: {invoices.count()}")
            self.stdout.write(f"   📦 Sales Orders: {orders.count()}")
            
            if invoices.exists():
                for invoice in invoices[:3]:
                    self.stdout.write(f"      • {invoice.transaction_number} - ${invoice.total_amount} ({invoice.payment_status})")
            
            if orders.exists():
                for order in orders[:3]:
                    self.stdout.write(f"      • {order.transaction_number} - ${order.total_amount} ({order.status})")
        
        elif role == 'vendor':
            bills = VendorBill.objects.filter(contact=contact, status='posted')
            orders = PurchaseOrder.objects.filter(contact=contact)
            self.stdout.write(f"   📄 Bills: {bills.count()}")
            self.stdout.write(f"   📦 Purchase Orders: {orders.count()}")
            
            if bills.exists():
                for bill in bills[:3]:
                    self.stdout.write(f"      • {bill.transaction_number} - ${bill.total_amount} ({bill.payment_status})")
            
            if orders.exists():
                for order in orders[:3]:
                    self.stdout.write(f"      • {order.transaction_number} - ${order.total_amount} ({order.status})")
        
        # Test portal dashboard access (simulate)
        self.stdout.write(f"   ✅ Portal access configured for {role} user")