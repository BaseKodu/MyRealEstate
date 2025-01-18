from django.shortcuts import render
from myrealestate.common.views import BaseUpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .forms import CompanySettingsForm
from .models import Company
from django.contrib import messages

# Create your views here.

def home(request):
    return render(request, 'home.html')


class CompanySettingsView(BaseUpdateView):
    model = Company
    form_class = CompanySettingsForm
    template_name = 'companies/settings.html'
    title = 'Company Settings'
    success_url = reverse_lazy('companies:home')

    def get_object(self):
        return self.get_company()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.get_company()  # Pass company to form
        return kwargs

    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            response = self.form_valid(form)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Settings updated successfully'
                })
            return response
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.company = self.get_company()
        response = super().form_valid(form)
        messages.success(self.request, 'Company settings updated successfully.')
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return field-specific errors for AJAX requests
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({
                'status': 'error',
                'errors': errors
            }, status=400)
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)