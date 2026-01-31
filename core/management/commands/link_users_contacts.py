from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import User, Contact


class Command(BaseCommand):
    help = 'Link existing portal users to contacts and create missing contacts'

    def handle(self, *args, **options):
        self.stdout.write("🔗 Linking Users to Contacts...")
        self.stdout.write("=" * 50)
        
        with transaction.atomic():
            # Get all portal users without contacts
            portal_users = User.objects.filter(role__in=['customer', 'vendor'], contact__isnull=True)
            
            for user in portal_users:
                self.stdout.write(f"Processing user: {user.email} ({user.role})")
                
                # Try to find existing contact with same email
                existing_contact = Contact.objects.filter(email=user.email).first()
                
                if existing_contact:
                    # Link existing contact to user
                    user.contact = existing_contact
                    # Update contact type to match user role
                    if existing_contact.contact_type != user.role:
                        existing_contact.contact_type = user.role
                        existing_contact.save()
                    user.save()
                    self.stdout.write(f"✅ Linked to existing contact: {existing_contact.name}")
                else:
                    # Create new contact for user
                    contact_name = f"{user.first_name} {user.last_name}".strip()
                    if not contact_name:
                        contact_name = user.email.split('@')[0].title()
                    
                    new_contact = Contact.objects.create(
                        name=contact_name,
                        email=user.email,
                        contact_type=user.role,
                        created_by_id=1  # Assume first admin user
                    )
                    user.contact = new_contact
                    user.save()
                    self.stdout.write(f"✅ Created new contact: {new_contact.name}")
            
            # Check for contacts without users
            unlinked_contacts = Contact.objects.filter(user_account__isnull=True)
            for contact in unlinked_contacts:
                self.stdout.write(f"📝 Contact without user: {contact.name} ({contact.email})")
        
        self.stdout.write("\n🎉 User-Contact linking completed!")
        
        # Show final status
        self.stdout.write("\n📊 Final Status:")
        linked_users = User.objects.filter(role__in=['customer', 'vendor'], contact__isnull=False).count()
        unlinked_users = User.objects.filter(role__in=['customer', 'vendor'], contact__isnull=True).count()
        self.stdout.write(f"Portal users with contacts: {linked_users}")
        self.stdout.write(f"Portal users without contacts: {unlinked_users}")