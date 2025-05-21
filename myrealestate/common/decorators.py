from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import getCurrentCompany

def company_required(view_func):
    """
    Decorator that adds current company to the view.
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            company = getCurrentCompany(request)
            # Add company to view kwargs
            kwargs['company'] = company
            return view_func(request, *args, **kwargs)
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('home')
    return _wrapped_view