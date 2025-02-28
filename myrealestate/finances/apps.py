from django.apps import AppConfig
from django.db.models.signals import post_migrate


class FinancesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myrealestate.finances'


    def ready(self):
        """
        Import signal handlers when Django is ready
        This is crucial to ensure signals are properly connected
        """
        # Import signal handlers
        import myrealestate.finances.signals

        # Connect post_migrate signal for existing companies
        post_migrate.connect(self.create_default_categories_for_existing, sender=self)
    
    def create_default_categories_for_existing(self, **kwargs):
        """
        Create default financial categories for existing companies after migration
        This ensures categories are created for companies that existed before this app was installed
        """
        from myrealestate.companies.models import Company
        from .utils import create_default_financial_categories, FinancialCategory
        
        # Get all companies
        companies = Company.objects.all()
        
        # For each company, check if they have categories, if not create them
        for company in companies:
            # Check if company already has categories
            has_categories = FinancialCategory.objects.filter(company=company).exists()
            if not has_categories:
                create_default_financial_categories(company)