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
    
    # Sales Orders
    path('sales-orders/', views.sales_order_list_view, name='sales_order_list'),
    path('sales-orders/create/', views.sales_order_create_view, name='sales_order_create'),
    
    # Customer Invoices
    path('customer-invoices/', views.customer_invoice_list_view, name='customer_invoice_list'),
    path('customer-invoices/create/', views.customer_invoice_create_view, name='customer_invoice_create'),
    path('customer-invoices/<int:pk>/post/', views.customer_invoice_post_view, name='customer_invoice_post'),
    
    # Payments
    path('payments/', views.payment_list_view, name='payment_list'),
    path('payments/create/', views.payment_create_view, name='payment_create'),
]
