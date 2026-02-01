from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('pdf/upload/', views.pdf_upload_view, name='pdf_upload'),
    path('pdf/list/', views.pdf_list_view, name='pdf_list'),
    path('pdf/<int:pk>/', views.pdf_detail_view, name='pdf_detail'),
    path('reports/generate/', views.generate_custom_report, name='generate_custom_report'),
]