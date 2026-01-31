from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import User, Contact


class Command(BaseCommand):
    help = 'Create a test portal user for testing'

    def add_arguments(self, parser):
        parser.add_argument('--type', choices=['customer', 'vendor'], default='customer', help='Type of user to create')
        parser.add_argument('--email', default='test@example.com', help='Email for the test user')

    def handle(self, *args, **options):
        user_type = options['type']
        email = options['email']
        
        try:
            with transaction.atomic():
                # Create contact first
                contact, created = Contact.objects.get_or_create(
                    email=email,
                    defaults={
                        'name': f'Test {user_type.title()}',
                        'contact_type': user_type,
                        'phone': '555-0123',
                        'address': '123 Test Street, Test City',
                    }
                )
                
                if created:
                    self.stdout.write(f"✅ Created contact: {contact.name}")
                else:
                    self.stdout.write(f"📋 Using existing contact: {contact.name}")
                
                # Create user
                username = email.split('@')[0]
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'login_id': username,
                        'first_name': 'Test',
                        'last_name': user_type.title(),
                        'role': user_type,
                        'contact': contact,
                    }
                )
                
                if created:
                    user.set_password('password123')
                    user.save()
                    self.stdout.write(f"✅ Created user: {user.username}")
                else:
                    # Update existing user
                    user.role = user_type
                    user.contact = contact
                    user.set_password('password123')
                    user.save()
                    self.stdout.write(f"🔄 Updated existing user: {user.username}")
                
                self.stdout.write("\n🎉 Test user created successfully!")
                self.stdout.write("=" * 40)
                self.stdout.write(f"📧 Email: {email}")
                self.stdout.write(f"🔑 Login ID: {user.login_id}")
                self.stdout.write(f"🔒 Password: password123")
                self.stdout.write(f"👤 Role: {user.get_role_display()}")
                self.stdout.write(f"🏢 Company: {contact.name}")
                self.stdout.write("\n🌐 Login at: http://127.0.0.1:8000/login/")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating test user: {str(e)}"))