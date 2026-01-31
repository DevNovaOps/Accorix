from django.core.management.base import BaseCommand
from core.models import User, Contact


class Command(BaseCommand):
    help = 'Check current users and their roles'

    def handle(self, *args, **options):
        self.stdout.write("👥 Current Users in System:")
        self.stdout.write("=" * 50)
        
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.WARNING("No users found in the system"))
            return
        
        for user in users:
            self.stdout.write(f"📧 Email: {user.email}")
            self.stdout.write(f"🔑 Login ID: {user.login_id}")
            self.stdout.write(f"👤 Username: {user.username}")
            self.stdout.write(f"🎭 Role: {user.role} ({user.get_role_display()})")
            self.stdout.write(f"🏢 Contact: {user.contact.name if user.contact else 'None'}")
            self.stdout.write(f"🔒 Is Portal User: {user.is_portal_user}")
            self.stdout.write(f"👑 Is Admin: {user.is_admin}")
            self.stdout.write("-" * 30)
        
        self.stdout.write("\n📊 Summary:")
        self.stdout.write(f"Total Users: {users.count()}")
        self.stdout.write(f"Admin Users: {users.filter(role='admin').count()}")
        self.stdout.write(f"Customer Users: {users.filter(role='customer').count()}")
        self.stdout.write(f"Vendor Users: {users.filter(role='vendor').count()}")
        self.stdout.write(f"Invoicing Users: {users.filter(role='invoicing').count()}")
        
        # Check contacts
        self.stdout.write("\n🏢 Contacts in System:")
        contacts = Contact.objects.all()
        for contact in contacts:
            linked_user = "Yes" if hasattr(contact, 'user_account') and contact.user_account else "No"
            self.stdout.write(f"• {contact.name} ({contact.contact_type}) - User Linked: {linked_user}")