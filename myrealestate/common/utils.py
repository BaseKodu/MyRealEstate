from django.core.exceptions import PermissionDenied
from myrealestate.companies.models import Company
import premailer
from django.template.loader import render_to_string
from pathlib import Path


def getCurrentCompany(request):
    """
    Returns the current company object based on the middleware-managed company details.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Company: The current company object
        
    Raises:
        PermissionDenied: If user has no company access or is not authenticated
    """
    if not request.user.is_authenticated:
        raise PermissionDenied('User must be authenticated to access company information.')

    company_details = request.company
    if not company_details:
        # Check if user has any companies at all
        companies = Company.objects.filter(
            usercompanyaccess__user=request.user
        ).distinct()
        
        if not companies.exists():
            raise PermissionDenied('User is not associated with any company.')
            
        # Trigger a refresh of company details
        request.refresh_company = True
        company = companies.first()
    else:
        try:
            company = Company.objects.get(id=company_details['id'])
        except Company.DoesNotExist:
            # If stored company ID is invalid, get first available company
            company = Company.objects.filter(
                usercompanyaccess__user=request.user
            ).first()
            if not company:
                raise PermissionDenied('User is not associated with any company.')
            # Trigger a refresh of company details
            request.refresh_company = True

    return company




def get_email_template(template_name, context):
    """
    Renders email template with inline CSS
    """
    css_path = Path(__file__).resolve().parent.parent / 'templates/emails/base/styles.css'
    with open(css_path) as f:
        css = f.read()
        
    context['styles'] = css
    html = render_to_string(template_name, context)
    
    # Inline CSS for email client compatibility
    inliner = premailer.Premailer(html)
    return inliner.transform()