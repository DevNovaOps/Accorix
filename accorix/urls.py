"""
URL configuration for accorix project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def root_webhook(request):
    """Handle webhook requests at root level - redirect to proper endpoint"""
    if request.method == 'GET':
        return JsonResponse({
            'error': 'Webhook endpoint moved',
            'correct_endpoint': '/payments/webhook/',
            'message': 'Please update your webhook URL to /payments/webhook/'
        }, status=404)
    else:
        return JsonResponse({'error': 'Webhook endpoint not found'}, status=404)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('transactions/', include('transactions.urls')),
    path('budgets/', include('budgets.urls')),
    path('portal/', include('portal.urls')),
    path('analytics/', include('analytics.urls')),
    path('payments/', include('payments.urls')),
    path('webhook/', root_webhook, name='root_webhook'),  # Handle old webhook URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
