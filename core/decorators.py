from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps


def admin_required(view_func):
    """Decorator to ensure only admin users can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def portal_user_required(view_func):
    """Decorator to ensure only portal users (customers/vendors) can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_portal_user:
            messages.error(request, 'Access denied. Portal users only.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def customer_required(view_func):
    """Decorator to ensure only customers can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'customer':
            messages.error(request, 'Access denied. Customers only.')
            return redirect('portal_dashboard' if request.user.is_portal_user else 'dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def vendor_required(view_func):
    """Decorator to ensure only vendors can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'vendor':
            messages.error(request, 'Access denied. Vendors only.')
            return redirect('portal_dashboard' if request.user.is_portal_user else 'dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_invoicing_required(view_func):
    """Decorator to ensure only admin or invoicing users can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role not in ['admin', 'invoicing']:
            messages.error(request, 'Access denied. Administrative privileges required.')
            return redirect('portal_dashboard' if request.user.is_portal_user else 'dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper