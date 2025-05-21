from django.shortcuts import render
from myrealestate.common.views import BaseUpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Company
from django.contrib import messages
from myrealestate.common.views import BaseListView
from myrealestate.common.views import BaseCreateView, CompanyRequiredMixin, CompanyViewMixin
from django.views import View
from django.utils.translation import gettext_lazy as _
from myrealestate.accounts.models import User, UserCompanyAccess, UserTypeEnums
from .forms import CompanySettingsForm
from .forms import UserInvitationForm
from .forms import UserCompanyAccessForm
from myrealestate.common.views import DeleteViewMixin
from icecream import ic
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
        kwargs['company'] = self.get_company() 
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
    

# views.py
class CompanyUsersView(BaseListView):
    template_name = "companies/company_users.html"
    model = UserCompanyAccess
    search_fields = ['user__email', 'user__username']
    ordering = "user__email"
    title = "Company Users"

    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.usercompanyaccess_set.first().company
        return queryset.filter(
            company=company
        ).select_related('user', 'company')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invitation_form'] = UserInvitationForm(
            company=self.request.user.usercompanyaccess_set.first().company,
            inviter=self.request.user
        )
        return context

    def has_add_permission(self):
        return self.request.user.usercompanyaccess_set.filter(
            company=self.request.user.usercompanyaccess_set.first().company,
            access_level=UserTypeEnums.COMPANY_OWNER
        ).exists()    

class InviteUserView(BaseCreateView):
    form_class = UserInvitationForm
    title = _("Invite User")
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'inviter': self.request.user,
            'request': self.request  # For building absolute URLs in the form
        })
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            ic("Form valid called")
            ic("Form valid response:", response)
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': _('Invitation sent successfully')
                })
            return response
        except Exception as e:
            ic("Exception:", e)
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
            raise

    def form_invalid(self, form):
        ic("Form invalid called")
        ic("Form errors:", form.errors)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':

            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)

class CheckEmailView(CompanyRequiredMixin, CompanyViewMixin, View):
    def get(self, request):
        email = request.GET.get('email')
        response_data = {
            'exists': False,
            'is_member': False,
            'error': None
        }
        
        if not email:
            response_data['error'] = _('Email is required')
            return JsonResponse(response_data, status=400)
            
        try:
            response_data['exists'] = User.objects.filter(email=email).exists()
            if response_data['exists']:
                response_data['is_member'] = UserCompanyAccess.objects.filter(
                    user__email=email,
                    company=self.get_company()
                ).exists()
            
            return JsonResponse(response_data)
            
        except Exception as e:
            response_data['error'] = str(e)
            return JsonResponse(response_data, status=500)
        
        


class UserCompanyAccessUpdateView(BaseUpdateView):
    model = UserCompanyAccess
    form_class = UserCompanyAccessForm
    title = _("Update User Access")

class UserCompanyAccessDeleteView(DeleteViewMixin, BaseUpdateView):
    model = UserCompanyAccess
    title = _("Delete User Access")