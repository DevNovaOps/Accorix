from django.core.management.base import BaseCommand
from budgets.models import BudgetFieldExplanation, BudgetStageMapping


class Command(BaseCommand):
    help = 'Seed budget field explanations and stage mappings'

    def handle(self, *args, **options):
        # Create field explanations
        field_explanations = [
            {
                'field_name': 'budget_name',
                'title': 'Budget Name',
                'explanation': 'Name assigned to the budget for easy identification and tracking purposes.',
                'example': 'Q1 2024 Marketing Budget, Annual IT Infrastructure Budget'
            },
            {
                'field_name': 'analytical_account',
                'title': 'Analytical Account',
                'explanation': 'Cost center or department where the budget will be allocated and tracked.',
                'example': 'Marketing Department, IT Infrastructure, Sales Operations'
            },
            {
                'field_name': 'budgeted_amount',
                'title': 'Budgeted Amount',
                'explanation': 'The planned or allocated amount for the specific period and analytical account.',
                'example': '₹50,000 for monthly marketing expenses, ₹2,00,000 for quarterly operations'
            },
            {
                'field_name': 'actual_amount',
                'title': 'Actual Amount',
                'explanation': 'The real amount spent or utilized from posted transactions during the budget period.',
                'example': 'Calculated from all posted invoices and bills within the budget period'
            },
            {
                'field_name': 'variance',
                'title': 'Variance',
                'explanation': 'Difference between actual and budgeted amounts. Positive means over-budget, negative means under-budget.',
                'example': '+₹5,000 (over-budget), -₹3,000 (under-budget)'
            },
            {
                'field_name': 'achievement_percentage',
                'title': 'Achievement Percentage',
                'explanation': 'Percentage of budget utilized. Helps track budget performance and utilization.',
                'example': '85% means 85% of the budget has been utilized'
            }
        ]

        for field_data in field_explanations:
            BudgetFieldExplanation.objects.get_or_create(
                field_name=field_data['field_name'],
                defaults=field_data
            )

        # Create stage mappings
        stage_mappings = [
            {
                'stage': 'planning',
                'description': 'Initial budget planning and preparation phase',
                'color_code': '#f59e0b',  # warning color
                'order': 1
            },
            {
                'stage': 'approved',
                'description': 'Budget has been reviewed and approved by management',
                'color_code': '#10b981',  # success color
                'order': 2
            },
            {
                'stage': 'active',
                'description': 'Budget is currently active and being utilized',
                'color_code': '#3b82f6',  # primary color
                'order': 3
            },
            {
                'stage': 'monitoring',
                'description': 'Budget performance is being actively monitored',
                'color_code': '#8b5cf6',  # secondary color
                'order': 4
            },
            {
                'stage': 'closed',
                'description': 'Budget period has ended and is closed for further transactions',
                'color_code': '#6b7280',  # muted color
                'order': 5
            }
        ]

        for stage_data in stage_mappings:
            BudgetStageMapping.objects.get_or_create(
                stage=stage_data['stage'],
                defaults=stage_data
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded budget field explanations and stage mappings')
        )