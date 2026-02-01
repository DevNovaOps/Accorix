from django.urls import path
from . import views

urlpatterns = [
    # Purchase Orders
    path('purchase-orders/', views.purchase_order_list_view, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create_view, name='purchase_order_create'),
    
    # Vendor Bills
    path('vendor-bills/', views.vendor_bill_list_view, name='vendor_bill_list'),
    path('vendor-bills/create/', views.vendor_bill_create_view, name='vendor_bill_create'),
    path('vendor-bills/<int:pk>/post/', views.vendor_bill_post_view, name='vendor_bill_post'),
    path('vendor-bills/<int:pk>/pdf/', views.vendor_bill_pdf, name='vendor_bill_pdf'),
    
    # Sales Orders
    path('sales-orders/', views.sales_order_list_view, name='sales_order_list'),
    path('sales-orders/create/', views.sales_order_create_view, name='sales_order_create'),
    
    # Customer Invoices
    path('customer-invoices/', views.customer_invoice_list_view, name='customer_invoice_list'),
    path('customer-invoices/create/', views.customer_invoice_create_view, name='customer_invoice_create'),
    path('customer-invoices/<int:pk>/post/', views.customer_invoice_post_view, name='customer_invoice_post'),
    path('customer-invoices/<int:pk>/pdf/', views.customer_invoice_pdf, name='customer_invoice_pdf'),
    
    # Payments
    path('payments/', views.payment_list_view, name='payment_list'),
    path('payments/create/', views.payment_create_view, name='payment_create'),
    
    # Chart of Accounts
    path('chart-of-accounts/', views.chart_of_accounts_list_view, name='chart_of_accounts_list'),
    path('chart-of-accounts/create/', views.chart_of_accounts_create_view, name='chart_of_accounts_create'),
    path('chart-of-accounts/<int:pk>/edit/', views.chart_of_accounts_edit_view, name='chart_of_accounts_edit'),
    
    # Bill Payments
    path('bill-payments/', views.bill_payment_list_view, name='bill_payment_list'),
    path('bill-payments/create/<int:bill_id>/', views.bill_payment_create_view, name='bill_payment_create'),
    
    # AJAX endpoints
    path('ajax/product-price/', views.get_product_price, name='get_product_price'),
    path('ajax/validate-budget/', views.validate_budget_ajax, name='validate_budget_ajax'),
    
    # Stripe Payment
    path('stripe-payment/<int:invoice_id>/', views.stripe_payment_view, name='stripe_payment'),
]
