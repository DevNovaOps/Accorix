from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Budget, BudgetRevision, BudgetFieldExplanation, BudgetStageMapping
from core.models import AnalyticalAccount
from .forms import BudgetForm


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
def budget_list_view(request):
    budgets = Budget.objects.filter(is_active=True).order_by('-start_date')
    return render(request, 'budgets/budget_list.html', {'budgets': budgets})


@login_required
def budget_create_view(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.created_by = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm()
    
    return render(request, 'budgets/budget_form.html', {
        'form': form,
        'title': 'Create Budget'
    })


@login_required
@user_passes_test(is_admin)
def budget_edit_view(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    
    if request.method == 'POST':
        old_amount = budget.budgeted_amount
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            new_amount = form.cleaned_data['budgeted_amount']
            if old_amount != new_amount:
                BudgetRevision.objects.create(
                    budget=budget,
                    previous_amount=old_amount,
                    new_amount=new_amount,
                    reason=request.POST.get('revision_reason', 'Budget updated'),
                    revised_by=request.user
                )
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)
    
    revisions = BudgetRevision.objects.filter(budget=budget).order_by('-revised_at')
    return render(request, 'budgets/budget_form.html', {
        'form': form,
        'title': 'Edit Budget',
        'budget': budget,
        'revisions': revisions
    })


@login_required
@user_passes_test(is_admin)
def budget_revise_view(request, pk):
    """Create a revision of an existing budget"""
    original_budget = get_object_or_404(Budget, pk=pk)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            # Create revision record
            old_amount = original_budget.budgeted_amount
            new_amount = form.cleaned_data['budgeted_amount']
            
            BudgetRevision.objects.create(
                budget=original_budget,
                previous_amount=old_amount,
                new_amount=new_amount,
                reason=request.POST.get('revision_reason', 'Budget revised'),
                revised_by=request.user
            )
            
            # Update the original budget
            original_budget.budgeted_amount = new_amount
            original_budget.notes = form.cleaned_data.get('notes', original_budget.notes)
            original_budget.stage = 'monitoring'  # Change stage to monitoring after revision
            original_budget.save()
            
            messages.success(request, 'Budget revised successfully!')
            return redirect('budget_comprehensive_dashboard')
    else:
        # Pre-populate form with original budget data
        form = BudgetForm(initial={
            'name': f"{original_budget.name} (Revised)",
            'analytical_account': original_budget.analytical_account,
            'start_date': original_budget.start_date,
            'end_date': original_budget.end_date,
            'budgeted_amount': original_budget.budgeted_amount,
            'status': 'draft',
            'stage': 'planning',
            'notes': original_budget.notes
        })
    
    return render(request, 'budgets/budget_revise_form.html', {
        'form': form,
        'original_budget': original_budget,
        'title': 'Revise Budget'
    })


@login_required
def budget_detail_view(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    revisions = BudgetRevision.objects.filter(budget=budget).order_by('-revised_at')
    
    return render(request, 'budgets/budget_detail.html', {
        'budget': budget,
        'revisions': revisions
    })


@login_required
def budget_dashboard_view(request):
    budgets = Budget.objects.filter(is_active=True).order_by('-start_date')
    
    # Calculate summary statistics
    total_budgeted = sum(b.budgeted_amount for b in budgets)
    total_actual = sum(b.actual_amount for b in budgets)
    total_variance = total_actual - total_budgeted
    overall_achievement = (total_actual / total_budgeted * 100) if total_budgeted > 0 else 0
    
    return render(request, 'budgets/budget_dashboard.html', {
        'budgets': budgets,
        'total_budgeted': total_budgeted,
        'total_actual': total_actual,
        'total_variance': total_variance,
        'overall_achievement': overall_achievement,
    })


@login_required
def budget_comprehensive_dashboard_view(request):
    """Comprehensive budget dashboard with 3-panel layout"""
    budgets = Budget.objects.filter(is_active=True).select_related('analytical_account').order_by('-start_date')
    
    # Get field explanations and stage mappings
    field_explanations = BudgetFieldExplanation.objects.filter(is_active=True)
    stage_mappings = BudgetStageMapping.objects.filter(is_active=True).order_by('order')
    
    # Calculate summary statistics
    total_budgeted = sum(b.budgeted_amount for b in budgets)
    total_actual = sum(b.actual_amount for b in budgets)
    total_variance = total_actual - total_budgeted
    overall_achievement = (total_actual / total_budgeted * 100) if total_budgeted > 0 else 0
    
    # Get partner information (example data)
    partner_info = {
        'name': 'Earnest Woodpecker',
        'total_budget': 250000,
        'utilized': 185000,
        'remaining': 65000,
        'achievement': 74
    }
    
    return render(request, 'budgets/budget_comprehensive_dashboard.html', {
        'budgets': budgets,
        'field_explanations': field_explanations,
        'stage_mappings': stage_mappings,
        'total_budgeted': total_budgeted,
        'total_actual': total_actual,
        'total_variance': total_variance,
        'overall_achievement': overall_achievement,
        'partner_info': partner_info,
    })
