from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # User Management
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.create_user_view, name='create_user'),
    
    # Master Data - Contacts
    path('contacts/', views.contact_list_view, name='contact_list'),
    path('contacts/create/', views.contact_create_view, name='contact_create'),
    path('contacts/<int:pk>/edit/', views.contact_edit_view, name='contact_edit'),
    path('contacts/<int:pk>/archive/', views.contact_archive_view, name='contact_archive'),
    
    # Master Data - Products
    path('products/', views.product_list_view, name='product_list'),
    path('products/create/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('products/<int:pk>/archive/', views.product_archive_view, name='product_archive'),
    
    # Master Data - Analytical Accounts
    path('analytical-accounts/', views.analytical_account_list_view, name='analytical_account_list'),
    path('analytical-accounts/create/', views.analytical_account_create_view, name='analytical_account_create'),
    path('analytical-accounts/<int:pk>/edit/', views.analytical_account_edit_view, name='analytical_account_edit'),
    path('analytical-accounts/<int:pk>/archive/', views.analytical_account_archive_view, name='analytical_account_archive'),
    
    # Master Data - Auto Analytical Models
    path('auto-analytical-models/', views.auto_analytical_model_list_view, name='auto_analytical_model_list'),
    path('auto-analytical-models/create/', views.auto_analytical_model_create_view, name='auto_analytical_model_create'),
    path('auto-analytical-models/<int:pk>/edit/', views.auto_analytical_model_edit_view, name='auto_analytical_model_edit'),
    path('auto-analytical-models/<int:pk>/archive/', views.auto_analytical_model_archive_view, name='auto_analytical_model_archive'),
]
