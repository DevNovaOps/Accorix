#!/usr/bin/env python
"""
ACCORIX Deployment Script
Handles database migrations, static files, and system checks
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accorix.settings')
django.setup()

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    try:
        import django
        import mysqlclient
        import stripe
        import matplotlib
        import pandas
        import numpy
        from PyPDF2 import PdfReader
        print("✅ All requirements are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def check_database():
    """Check database connection"""
    print("🔍 Checking database connection...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Please check your database settings in settings.py")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        'media',
        'media/documents',
        'media/charts',
        'media/contacts',
        'media/products',
        'staticfiles',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {directory}")
    
    print("✅ Directories created")

def main():
    """Main deployment function"""
    print("🚀 Starting ACCORIX Deployment...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check database
    if not check_database():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        sys.exit(1)
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("⚠️  Static files collection failed, but continuing...")
    
    # Run system checks
    if not run_command("python manage.py check", "Running system checks"):
        print("⚠️  System checks failed, but continuing...")
    
    # Check if setup script should be run
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(is_superuser=True).exists():
        print("\n🔧 No admin users found. Running setup script...")
        if run_command("python setup_complete_system.py", "Setting up sample data"):
            print("✅ Sample data created successfully")
        else:
            print("⚠️  Setup script failed. You may need to create users manually.")
    else:
        print("✅ Admin users already exist")
    
    print("=" * 50)
    print("🎉 ACCORIX Deployment Complete!")
    print("\n📋 Next Steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Access the application: http://localhost:8000")
    print("3. Login with admin credentials")
    print("\n🔧 Configuration:")
    print("- Update Stripe keys in settings.py for payments")
    print("- Configure email settings for notifications")
    print("- Set up SSL certificate for production")
    print("\n📚 Documentation: README.md")

if __name__ == '__main__':
    main()