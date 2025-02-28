from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from myrealestate.companies.models import Company
from .models import (
    PropertyPurchase, 
    PropertyBond, 
    FinancialTransaction, 
    FinancialCategory,
)

from .utils import create_default_financial_categories

@receiver(post_save, sender=Company)
def create_company_financial_categories(sender, instance, created, **kwargs):
    """
    Create default financial categories when a new company is created
    """
    if created:
        create_default_financial_categories(instance)

# Other signal handlers (for PropertyPurchase, PropertyBond, etc.)
# ...