# mixins.py
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .utils import getCurrentCompany

class PatchHandlerMixin:
    """
    Mixin to handle PATCH requests through POST method with a hidden _method field.
    Returns rendered template instead of JSON.
    """
    def post(self, request, *args, **kwargs):
        if request.POST.get('_method') == 'PATCH':
            if hasattr(self, 'patch'):
                return self.patch(request, *args, **kwargs)
            return HttpResponseBadRequest('PATCH method not implemented')
        return super().post(request, *args, **kwargs)

class CompanyRequiredMixin(LoginRequiredMixin):
    """
    Mixin that adds current company to the view.
    Must be used with View classes.
    """
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.company = getCurrentCompany(request)
        except PermissionDenied as e:
            messages.error(request, str(e))
            self.handle_no_company()

    def handle_no_company(self):
        """Override this method to customize the no-company behavior"""
        raise PermissionDenied("No company access")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.company
        return context