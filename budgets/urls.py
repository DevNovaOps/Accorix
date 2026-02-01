from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_dashboard_view, name='budget_dashboard'),
    path('comprehensive/', views.budget_comprehensive_dashboard_view, name='budget_comprehensive_dashboard'),
    path('list/', views.budget_list_view, name='budget_list'),
    path('create/', views.budget_create_view, name='budget_create'),
    path('<int:pk>/', views.budget_detail_view, name='budget_detail'),
    path('<int:pk>/edit/', views.budget_edit_view, name='budget_edit'),
    path('<int:pk>/revise/', views.budget_revise_view, name='budget_revise'),
]
