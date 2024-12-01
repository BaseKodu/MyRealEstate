# mixins.py
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .utils import getCurrentCompany



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