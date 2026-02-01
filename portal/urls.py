from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_dashboard_view, name='portal_dashboard'),
    path('invoices/', views.portal_invoices_view, name='portal_invoices'),
    path('invoices/<int:pk>/', views.portal_invoice_detail_view, name='portal_invoice_detail'),
    path('invoices/<int:pk>/pdf/', views.portal_invoice_pdf, name='portal_invoice_pdf'),
    path('bills/', views.portal_bills_view, name='portal_bills'),
    path('bills/<int:pk>/', views.portal_bill_detail_view, name='portal_bill_detail'),
    path('bills/<int:pk>/pdf/', views.portal_bill_pdf, name='portal_bill_pdf'),
    path('orders/', views.portal_orders_view, name='portal_orders'),
    path('payment/', views.portal_payment_view, name='portal_payment'),
    path('payment/invoice/<int:invoice_id>/', views.portal_payment_view, name='portal_payment_invoice'),
    path('payment/bill/<int:bill_id>/', views.portal_payment_view, name='portal_payment_bill'),
]
