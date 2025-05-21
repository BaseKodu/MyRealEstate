from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from myrealestate.accounts.models import User
from myrealestate.companies.models import Company


def company_dict(company: Company, user: User) -> dict:
    return {
        'id': company.id,
        'name': company.name,
    }


@receiver(user_logged_in)
def store_company_details(sender, user: User, request, **kwargs):
    if user.is_authenticated:
        companies = Company.objects.filter(
            usercompanyaccess__user=user
        ).distinct()
        
        if companies.exists():
            company = companies.first()
            request.session['company'] = company_dict(company, user)
            request.session['current_company_id'] = company.id
        else:
            request.session['company'] = None
            request.session['current_company_id'] = None


class CompanyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        company_details = request.session.get('company')

        if getattr(request, 'refresh_company', False):
            company_details = self.refresh_company_details(request)

        request.company = company_details if company_details else None

    def refresh_company_details(self, request):
        user = request.user
        if user.is_authenticated:
            companies = Company.objects.filter(
                usercompanyaccess__user=user
            ).distinct()
            
            if companies.exists():
                # Try to get current company from session, fall back to first company
                current_company_id = request.session.get('current_company_id')
                try:
                    company = companies.get(id=current_company_id)
                except Company.DoesNotExist:
                    company = companies.first()
                
                company_details = company_dict(company, user)
                request.session['company'] = company_details
                request.session['current_company_id'] = company.id
                return company_details
        
        request.session['company'] = None
        request.session['current_company_id'] = None
        return None