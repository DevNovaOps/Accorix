#!/usr/bin/env python3
"""
ACCORIX ERP - Production Setup Script
This script helps set up the system for production deployment
"""

import os
import sys
import django
import secrets
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accorix.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from core.models import Contact, Product, AnalyticalAccount
from transactions.models import ChartOfAccounts
from budgets.models import Budget

User = get_user_model()

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n[{step}] {description}")

def generate_secret_key():
    """Generate a secure Django secret key"""
    return secrets.token_urlsafe(50)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = BASE_DIR / '.env'
    env_example = BASE_DIR / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        print_step("ENV", "Creating .env file from template...")
        
        # Read template
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Generate secret key
        secret_key = generate_secret_key()
        content = content.replace('your-super-secret-django-key-here', secret_key)
        
        # Write .env file
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created successfully!")
        print("⚠️  Please update the .env file with your actual configuration values.")
        return True
    elif env_file.exists():
        print_step("ENV", ".env file already exists")
        return True
    else:
        print_step("ENV", "❌ .env.example not found. Please create .env manually.")
        return False

def run_migrations():
    """Run database migrations"""
    print_step("DB", "Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_superuser():
    """Create superuser if none exists"""
    print_step("USER", "Checking for superuser...")
    
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superuser already exists")
        return True
    
    print("Creating superuser...")
    try:
        username = input("Enter superuser username: ").strip()
        email = input("Enter superuser email: ").strip()
        password = input("Enter superuser password: ").strip()
        
        if not all([username, email, password]):
            print("❌ All fields are required")
            return False
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name="System",
            last_name="Administrator",
            role="admin"
        )
        print("✅ Superuser created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        return False

def setup_basic_data():
    """Set up basic system data"""
    print_step("DATA", "Setting up basic system data...")
    
    try:
        # Create basic chart of accounts
        accounts_data = [
            ('1000', 'Cash and Cash Equivalents', 'assets'),
            ('1100', 'Bank Account - Main', 'assets'),
            ('1200', 'Accounts Receivable', 'assets'),
            ('2000', 'Accounts Payable', 'liabilities'),
            ('3000', 'Owner Equity', 'equity'),
            ('4000', 'Sales Revenue', 'income'),
            ('5000', 'Cost of Goods Sold', 'expense'),
            ('6000', 'Operating Expenses', 'expense'),
        ]
        
        for code, name, acc_type in accounts_data:
            ChartOfAccounts.objects.get_or_create(
                account_code=code,
                defaults={
                    'account_name': name,
                    'account_type': acc_type,
                    'status': 'confirmed',
                    'is_active': True
                }
            )
        
        # Create basic analytical accounts
        analytical_accounts = [
            ('SALES', 'Sales Department'),
            ('MARKETING', 'Marketing Department'),
            ('IT', 'IT Department'),
            ('ADMIN', 'Administration'),
        ]
        
        for code, name in analytical_accounts:
            AnalyticalAccount.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'status': 'confirmed',
                    'is_active': True
                }
            )
        
        print("✅ Basic system data created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create basic data: {e}")
        return False

def collect_static_files():
    """Collect static files for production"""
    print_step("STATIC", "Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to collect static files: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print_step("DIRS", "Creating necessary directories...")
    
    directories = [
        BASE_DIR / 'logs',
        BASE_DIR / 'media',
        BASE_DIR / 'media' / 'documents',
        BASE_DIR / 'media' / 'charts',
        BASE_DIR / 'staticfiles',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def check_stripe_config():
    """Check Stripe configuration"""
    print_step("STRIPE", "Checking Stripe configuration...")
    
    from django.conf import settings
    
    if (settings.STRIPE_PUBLISHABLE_KEY.startswith('pk_') and 
        settings.STRIPE_SECRET_KEY.startswith('sk_')):
        print("✅ Stripe keys are configured")
        
        if settings.STRIPE_WEBHOOK_SECRET.startswith('whsec_'):
            print("✅ Stripe webhook secret is configured")
        else:
            print("⚠️  Stripe webhook secret needs to be configured")
        
        return True
    else:
        print("⚠️  Stripe keys need to be configured in .env file")
        return False

def run_system_checks():
    """Run Django system checks"""
    print_step("CHECK", "Running system checks...")
    try:
        execute_from_command_line(['manage.py', 'check'])
        print("✅ System checks passed!")
        return True
    except Exception as e:
        print(f"❌ System checks failed: {e}")
        return False

def main():
    """Main setup function"""
    print_header("ACCORIX ERP - Production Setup")
    print("This script will help you set up ACCORIX ERP for production deployment.")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    steps = [
        ("Create directories", create_directories),
        ("Create .env file", create_env_file),
        ("Run migrations", run_migrations),
        ("Create superuser", create_superuser),
        ("Setup basic data", setup_basic_data),
        ("Collect static files", collect_static_files),
        ("Check Stripe config", check_stripe_config),
        ("Run system checks", run_system_checks),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        try:
            if step_func():
                success_count += 1
        except KeyboardInterrupt:
            print("\n\n❌ Setup interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error in {step_name}: {e}")
    
    # Summary
    print_header("SETUP SUMMARY")
    print(f"Completed: {success_count}/{total_steps} steps")
    
    if success_count == total_steps:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your actual configuration")
        print("2. Configure your web server (Nginx/Apache)")
        print("3. Set up SSL certificate")
        print("4. Configure Stripe webhooks")
        print("5. Test the application")
    else:
        print(f"\n⚠️  Setup completed with {total_steps - success_count} issues")
        print("Please review the errors above and fix them before proceeding.")
    
    print("\nFor detailed instructions, see:")
    print("- STRIPE_INTEGRATION_GUIDE.md")
    print("- DEPLOYMENT_CHECKLIST.md")

if __name__ == '__main__':
    main()