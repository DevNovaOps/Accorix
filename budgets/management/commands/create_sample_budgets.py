from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from budgets.models import Budget
from core.models import AnalyticalAccount, User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample budget data for testing'

    def handle(self, *args, **options):
        # Get or create analytical accounts
        marketing_account, _ = AnalyticalAccount.objects.get_or_create(
            code='MKT001',
            defaults={
                'name': 'Marketing Department',
                'description': 'Marketing and advertising expenses',
                'status': 'confirmed'
            }
        )
        
        it_account, _ = AnalyticalAccount.objects.get_or_create(
            code='IT001',
            defaults={
                'name': 'IT Infrastructure',
                'description': 'Information technology infrastructure costs',
                'status': 'confirmed'
            }
        )
        
        sales_account, _ = AnalyticalAccount.objects.get_or_create(
            code='SAL001',
            defaults={
                'name': 'Sales Operations',
                'description': 'Sales team operations and expenses',
                'status': 'confirmed'
            }
        )

        # Get admin user
        admin_user = User.objects.filter(role='admin').first()
        if not admin_user:
            admin_user = User.objects.filter(is_superuser=True).first()

        # Create sample budgets
        budgets_data = [
            {
                'name': 'Q1 2024 Marketing Budget',
                'analytical_account': marketing_account,
                'start_date': datetime(2024, 1, 1).date(),
                'end_date': datetime(2024, 3, 31).date(),
                'budgeted_amount': Decimal('150000'),
                'status': 'confirmed',
                'stage': 'active',
                'notes': 'Quarterly marketing budget for digital campaigns and events'
            },
            {
                'name': 'Annual IT Infrastructure 2024',
                'analytical_account': it_account,
                'start_date': datetime(2024, 1, 1).date(),
                'end_date': datetime(2024, 12, 31).date(),
                'budgeted_amount': Decimal('500000'),
                'status': 'confirmed',
                'stage': 'monitoring',
                'notes': 'Annual budget for IT infrastructure upgrades and maintenance'
            },
            {
                'name': 'Sales Team Q2 Budget',
                'analytical_account': sales_account,
                'start_date': datetime(2024, 4, 1).date(),
                'end_date': datetime(2024, 6, 30).date(),
                'budgeted_amount': Decimal('200000'),
                'status': 'draft',
                'stage': 'planning',
                'notes': 'Q2 budget for sales team operations and incentives'
            },
            {
                'name': 'Marketing Campaign - Summer 2024',
                'analytical_account': marketing_account,
                'start_date': datetime(2024, 6, 1).date(),
                'end_date': datetime(2024, 8, 31).date(),
                'budgeted_amount': Decimal('75000'),
                'status': 'confirmed',
                'stage': 'approved',
                'notes': 'Summer marketing campaign budget'
            },
            {
                'name': 'IT Security Upgrade',
                'analytical_account': it_account,
                'start_date': datetime(2024, 3, 1).date(),
                'end_date': datetime(2024, 5, 31).date(),
                'budgeted_amount': Decimal('100000'),
                'status': 'archived',
                'stage': 'closed',
                'notes': 'Security infrastructure upgrade project - completed'
            }
        ]

        for budget_data in budgets_data:
            budget, created = Budget.objects.get_or_create(
                name=budget_data['name'],
                analytical_account=budget_data['analytical_account'],
                defaults={
                    **budget_data,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f"Created budget: {budget.name}")
            else:
                self.stdout.write(f"Budget already exists: {budget.name}")

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample budget data')
        )