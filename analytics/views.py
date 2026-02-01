import json
import io
import base64
from datetime import datetime, timedelta
from decimal import Decimal

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from PyPDF2 import PdfReader

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.files.base import ContentFile

from core.models import User, Contact
from transactions.models import CustomerInvoice, VendorBill, Payment, SalesOrder, PurchaseOrder
from budgets.models import Budget
from .models import PDFDocument, AnalyticsReport
from .forms import PDFUploadForm, AnalyticsReportForm


def is_admin_or_invoicing(user):
    return user.is_authenticated and user.role in ['admin', 'invoicing']


@login_required
@user_passes_test(is_admin_or_invoicing)
def analytics_dashboard(request):
    """Main analytics dashboard with charts and KPIs"""
    # Get date range (default to last 12 months)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Revenue vs Expense Chart
    revenue_chart = generate_revenue_expense_chart(start_date, end_date)
    
    # Monthly Trends Chart
    monthly_trends_chart = generate_monthly_trends_chart(start_date, end_date)
    
    # Top Customers Chart
    top_customers_chart = generate_top_customers_chart()
    
    # Budget Variance Chart
    budget_variance_chart = generate_budget_variance_chart()
    
    # KPIs
    invoices = CustomerInvoice.objects.filter(
        status='posted', 
        date__range=[start_date, end_date]
    )
    bills = VendorBill.objects.filter(
        status='posted', 
        date__range=[start_date, end_date]
    )
    
    total_revenue = sum(invoice.total_amount for invoice in invoices)
    total_expenses = sum(bill.total_amount for bill in bills)
    net_profit = total_revenue - total_expenses
    
    outstanding_invoices_qs = CustomerInvoice.objects.filter(
        status='posted',
        payment_status__in=['not_paid', 'partially_paid']
    )
    outstanding_invoices = sum(invoice.remaining_amount for invoice in outstanding_invoices_qs)
    
    context = {
        'revenue_chart': revenue_chart,
        'monthly_trends_chart': monthly_trends_chart,
        'top_customers_chart': top_customers_chart,
        'budget_variance_chart': budget_variance_chart,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'outstanding_invoices': outstanding_invoices,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'analytics/dashboard.html', context)


def generate_revenue_expense_chart(start_date, end_date):
    """Generate revenue vs expense comparison chart"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Get monthly data
    months = []
    revenues = []
    expenses = []
    
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        # Get invoices for this month and calculate total
        month_invoices = CustomerInvoice.objects.filter(
            status='posted',
            date__range=[current_date, next_month - timedelta(days=1)]
        )
        month_revenue = sum(invoice.total_amount for invoice in month_invoices)
        
        # Get bills for this month and calculate total
        month_bills = VendorBill.objects.filter(
            status='posted',
            date__range=[current_date, next_month - timedelta(days=1)]
        )
        month_expense = sum(bill.total_amount for bill in month_bills)
        
        months.append(current_date.strftime('%b %Y'))
        revenues.append(float(month_revenue))
        expenses.append(float(month_expense))
        
        current_date = next_month
    
    x = np.arange(len(months))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, revenues, width, label='Revenue', color='#4CAF50', alpha=0.8)
    bars2 = ax.bar(x + width/2, expenses, width, label='Expenses', color='#f44336', alpha=0.8)
    
    ax.set_xlabel('Month', color='white')
    ax.set_ylabel('Amount (₹)', color='white')
    ax.set_title('Revenue vs Expenses', color='white', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45, ha='right', color='white')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Format y-axis to show currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    ax.tick_params(colors='white')
    
    plt.tight_layout()
    
    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', facecolor='#1a1a1a', edgecolor='none', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    return graphic


def generate_monthly_trends_chart(start_date, end_date):
    """Generate monthly trends line chart"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Get monthly data
    months = []
    revenues = []
    expenses = []
    profits = []
    
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        # Get invoices for this month and calculate total
        month_invoices = CustomerInvoice.objects.filter(
            status='posted',
            date__range=[current_date, next_month - timedelta(days=1)]
        )
        month_revenue = sum(invoice.total_amount for invoice in month_invoices)
        
        # Get bills for this month and calculate total
        month_bills = VendorBill.objects.filter(
            status='posted',
            date__range=[current_date, next_month - timedelta(days=1)]
        )
        month_expense = sum(bill.total_amount for bill in month_bills)
        
        months.append(current_date)
        revenues.append(float(month_revenue))
        expenses.append(float(month_expense))
        profits.append(float(month_revenue - month_expense))
        
        current_date = next_month
    
    ax.plot(months, revenues, marker='o', linewidth=2, label='Revenue', color='#4CAF50')
    ax.plot(months, expenses, marker='s', linewidth=2, label='Expenses', color='#f44336')
    ax.plot(months, profits, marker='^', linewidth=2, label='Profit', color='#2196F3')
    
    ax.set_xlabel('Month', color='white')
    ax.set_ylabel('Amount (₹)', color='white')
    ax.set_title('Monthly Financial Trends', color='white', fontsize=16, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Format dates on x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='white')
    
    # Format y-axis to show currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    ax.tick_params(colors='white')
    
    plt.tight_layout()
    
    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', facecolor='#1a1a1a', edgecolor='none', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    return graphic


def generate_top_customers_chart():
    """Generate top customers pie chart"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Get all posted invoices grouped by customer
    from collections import defaultdict
    customer_totals = defaultdict(Decimal)
    
    invoices = CustomerInvoice.objects.filter(status='posted').select_related('contact')
    for invoice in invoices:
        customer_totals[invoice.contact.name] += invoice.total_amount
    
    # Get top 10 customers
    top_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    
    if top_customers:
        labels = [customer[0] for customer in top_customers]
        sizes = [float(customer[1]) for customer in top_customers]
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        # Customize text colors
        for text in texts:
            text.set_color('white')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    else:
        ax.text(0.5, 0.5, 'No customer data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, color='white', fontsize=14)
    
    ax.set_title('Top Customers by Revenue', color='white', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    
    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', facecolor='#1a1a1a', edgecolor='none', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    return graphic


def generate_budget_variance_chart():
    """Generate budget variance chart"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    budgets = Budget.objects.filter(is_active=True)
    
    if budgets:
        budget_names = [budget.name for budget in budgets]
        budgeted_amounts = [float(budget.budgeted_amount) for budget in budgets]
        actual_amounts = [float(budget.actual_amount) for budget in budgets]
        
        x = np.arange(len(budget_names))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, budgeted_amounts, width, label='Budgeted', color='#2196F3', alpha=0.8)
        bars2 = ax.bar(x + width/2, actual_amounts, width, label='Actual', color='#FF9800', alpha=0.8)
        
        ax.set_xlabel('Budget Categories', color='white')
        ax.set_ylabel('Amount (₹)', color='white')
        ax.set_title('Budget vs Actual Spending', color='white', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(budget_names, rotation=45, ha='right', color='white')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format y-axis to show currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
        ax.tick_params(colors='white')
    else:
        ax.text(0.5, 0.5, 'No budget data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, color='white', fontsize=14)
    
    plt.tight_layout()
    
    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', facecolor='#1a1a1a', edgecolor='none', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    return graphic


@login_required
def pdf_upload_view(request):
    """Upload and process PDF documents"""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_doc = form.save(commit=False)
            pdf_doc.uploaded_by = request.user
            
            # Extract text from PDF
            try:
                pdf_file = request.FILES['pdf_file']
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                
                pdf_doc.extracted_text = text
                
                # Simple amount extraction (you can enhance this with regex patterns)
                import re
                amount_pattern = r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
                amounts = re.findall(amount_pattern, text)
                if amounts:
                    # Take the largest amount found
                    amounts = [float(amt.replace(',', '')) for amt in amounts]
                    pdf_doc.extracted_amount = max(amounts)
                
                # Simple date extraction
                date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
                dates = re.findall(date_pattern, text)
                if dates:
                    try:
                        from datetime import datetime
                        pdf_doc.extracted_date = datetime.strptime(dates[0], '%d/%m/%Y').date()
                    except:
                        pass
                
                pdf_doc.processed = True
                
            except Exception as e:
                messages.warning(request, f'PDF uploaded but text extraction failed: {str(e)}')
            
            pdf_doc.save()
            messages.success(request, 'PDF uploaded and processed successfully!')
            return redirect('pdf_list')
    else:
        form = PDFUploadForm()
    
    return render(request, 'analytics/pdf_upload.html', {'form': form})


@login_required
def pdf_list_view(request):
    """List uploaded PDF documents"""
    documents = PDFDocument.objects.all()
    if not request.user.role == 'admin':
        documents = documents.filter(uploaded_by=request.user)
    
    return render(request, 'analytics/pdf_list.html', {'documents': documents})


@login_required
def pdf_detail_view(request, pk):
    """View PDF document details"""
    document = get_object_or_404(PDFDocument, pk=pk)
    
    # Check permissions
    if not request.user.role == 'admin' and document.uploaded_by != request.user:
        messages.error(request, 'Access denied.')
        return redirect('pdf_list')
    
    return render(request, 'analytics/pdf_detail.html', {'document': document})


@login_required
@user_passes_test(is_admin_or_invoicing)
def generate_custom_report(request):
    """Generate custom analytics report"""
    if request.method == 'POST':
        form = AnalyticsReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.generated_by = request.user
            
            # Generate chart based on report type
            chart_data = None
            if report.report_type == 'revenue':
                chart_data = generate_revenue_analysis_chart(report.start_date, report.end_date)
            elif report.report_type == 'expense':
                chart_data = generate_expense_analysis_chart(report.start_date, report.end_date)
            elif report.report_type == 'profit_loss':
                chart_data = generate_profit_loss_chart(report.start_date, report.end_date)
            
            if chart_data:
                # Save chart as image
                image_data = base64.b64decode(chart_data)
                image_file = ContentFile(image_data, name=f'{report.name}_{report.report_type}.png')
                report.chart_image.save(f'{report.name}_{report.report_type}.png', image_file)
            
            report.save()
            messages.success(request, 'Report generated successfully!')
            return redirect('analytics_dashboard')
    else:
        form = AnalyticsReportForm()
    
    return render(request, 'analytics/generate_report.html', {'form': form})


def generate_revenue_analysis_chart(start_date, end_date):
    """Generate detailed revenue analysis chart"""
    # Implementation similar to other chart functions
    return generate_revenue_expense_chart(start_date, end_date)


def generate_expense_analysis_chart(start_date, end_date):
    """Generate detailed expense analysis chart"""
    # Implementation for expense analysis
    return generate_revenue_expense_chart(start_date, end_date)


def generate_profit_loss_chart(start_date, end_date):
    """Generate profit & loss chart"""
    # Implementation for P&L analysis
    return generate_monthly_trends_chart(start_date, end_date)