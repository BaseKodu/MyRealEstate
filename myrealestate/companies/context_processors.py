from .models import Company

def company_context(request):
    context = {
        'current_company': None,
        'companies': []
    }
    
    if not request.user.is_authenticated:
        return context

    # Get companies from database
    companies = Company.objects.filter(
        usercompanyaccess__user=request.user
    ).distinct()
    
    # Get current company using the middleware-managed session
    company_details = request.company
    current_company = None
    
    if company_details:
        try:
            current_company = companies.get(id=company_details['id'])
        except Company.DoesNotExist:
            # Fallback to first company if stored company is no longer accessible
            current_company = companies.first()
            if current_company:
                # Trigger middleware refresh
                request.refresh_company = True
    
    context.update({
        'current_company': current_company,
        'companies': companies
    })
    
    return context