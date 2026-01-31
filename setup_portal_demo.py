#!/usr/bin/env python
"""
Setup script for portal demo data
Run this after migrations to create sample data for testing portal functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accorix.settings')
django.setup()

from django.core.management import call_command
from django.db import transaction
from core.models import User, Contact

def main():
    print("🚀 Setting up Portal Demo Data...")
    
    try:
        # Run migrations first
        print("📦 Running migrations...")
        call_command('migrate', verbosity=0)
        
        # Migrate existing portal users if any
        print("🔄 Migrating existing portal users...")
        call_command('migrate_portal_users', verbosity=1)
        
        # Create sample data
        print("📊 Creating sample data...")
        call_command('create_sample_data', verbosity=1)
        
        # Display created users
        print("\n✅ Demo setup completed!")
        print("\n👥 Portal Users Created:")
        print("-" * 50)
        
        portal_users = User.objects.filter(role__in=['customer', 'vendor'])
        for user in portal_users:
            print(f"📧 Email: {user.email}")
            print(f"🔑 Login ID: {user.login_id}")
            print(f"👤 Role: {user.get_role_display()}")
            print(f"🏢 Company: {user.contact.name if user.contact else 'N/A'}")
            print(f"🔒 Password: password123")
            print("-" * 30)
        
        print("\n🌐 Portal Access:")
        print("Customers can see: Invoices, Sales Orders, Payment options")
        print("Vendors can see: Bills, Purchase Orders")
        print("\n💡 Login at: /login/")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())