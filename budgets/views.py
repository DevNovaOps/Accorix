from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Budget, BudgetRevision
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
