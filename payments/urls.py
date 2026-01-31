from django.urls import path
from . import views

urlpatterns = [
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('pay/<int:invoice_id>/', views.payment_page, name='payment_page'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('cancel/<int:payment_id>/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('webhook/test/', views.webhook_test, name='webhook_test'),
    path('webhook/status/', views.webhook_status, name='webhook_status'),
    path('history/', views.payment_history, name='payment_history'),
]