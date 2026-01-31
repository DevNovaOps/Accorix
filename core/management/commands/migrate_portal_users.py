from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import User, Contact


class Command(BaseCommand):
    help = 'Migrate existing portal users to new role structure (customer/vendor)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find all portal users
        portal_users = User.objects.filter(role='portal')
        
        if not portal_users.exists():
            self.stdout.write(self.style.SUCCESS('No portal users found to migrate'))
            return
        
        self.stdout.write(f'Found {portal_users.count()} portal users to migrate')
        
        migrated_count = 0
        error_count = 0
        
        for user in portal_users:
            try:
                # Try to find matching contact by email
                contact = Contact.objects.filter(email=user.email).first()
                
                if contact:
                    # Determine role based on contact type
                    if contact.contact_type == 'customer':
                        new_role = 'customer'
                    elif contact.contact_type == 'vendor':
                        new_role = 'vendor'
                    elif contact.contact_type == 'both':
                        # Default to customer for 'both' type
                        new_role = 'customer'
                        self.stdout.write(
                            self.style.WARNING(
                                f'Contact {contact.name} has type "both", defaulting to customer role'
                            )
                        )
                    else:
                        new_role = 'customer'  # Default fallback
                    
                    if not dry_run:
                        with transaction.atomic():
                            user.role = new_role
                            user.contact = contact
                            user.save()
                    
                    self.stdout.write(
                        f'{"[DRY RUN] " if dry_run else ""}Migrated user {user.username} '
                        f'({user.email}) to {new_role} role, linked to contact {contact.name}'
                    )
                    migrated_count += 1
                    
                else:
                    # No matching contact found
                    self.stdout.write(
                        self.style.ERROR(
                            f'No contact found for user {user.username} ({user.email}). '
                            f'Please create a contact first or link manually.'
                        )
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error migrating user {user.username}: {str(e)}')
                )
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Migration Summary:')
        self.stdout.write(f'  Successfully migrated: {migrated_count}')
        self.stdout.write(f'  Errors: {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. Use --dry-run=False to apply changes.'))
        else:
            self.stdout.write(self.style.SUCCESS('\nMigration completed!'))