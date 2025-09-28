from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(function=None, redirect_url='core:home'):
    """
    Decorator for views that checks that the user is an admin (is_staff),
    redirecting to the specified page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=redirect_url
    )
    
    if function:
        return actual_decorator(function)
    
    return actual_decorator

def superuser_required(function=None, redirect_url='core:home'):
    """
    Decorator for views that checks that the user is a superuser,
    redirecting to the specified page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=redirect_url
    )
    
    if function:
        return actual_decorator(function)
    
    return actual_decorator