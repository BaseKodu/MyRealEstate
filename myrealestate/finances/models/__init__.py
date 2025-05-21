from .enums import (
    CategoryType, PropertyType, PurchaseType, InterestRateType,
    TransactionType, PaymentMethod, RecurrenceFrequency
)

from .categories import FinancialCategory
from .property_purchase import PropertyPurchase
from .property_bond import PropertyBond
from .municipal_account import MunicipalAccount
from .body_corporate import BodyCorporate
from .transactions import FinancialTransaction
from .recurring_transactions import RecurringTransaction

# Define what's available when using 'from myrealestate.finances.models import *'
__all__ = [
    'CategoryType', 'PropertyType', 'PurchaseType', 'InterestRateType',
    'TransactionType', 'PaymentMethod', 'RecurrenceFrequency',
    'FinancialCategory', 'PropertyPurchase', 'PropertyBond',
    'MunicipalAccount', 'BodyCorporate', 'FinancialTransaction',
    'RecurringTransaction'
]











'''
# Create default financial categories for South African property management
def create_default_financial_categories(company):
    """
    Creates default financial categories for a new company
    """
    # Income categories
    income_categories = [
        {"name": "Rental Income", "description": "Regular rental income from tenants"},
        {"name": "Parking Income", "description": "Income from parking spots or garages"},
        {"name": "Deposit Income", "description": "Income from tenant deposits"},
        {"name": "Utility Recovery", "description": "Recovery of utility costs from tenants"},
        {"name": "Late Fee Income", "description": "Income from late payment fees"},
        {"name": "Interest Income", "description": "Interest earned on deposits or investments"},
    ]
    
    # Expense categories - South African specific
    expense_categories = [
        {"name": "Municipal Rates", "description": "Property rates paid to municipality", "is_tax_deductible": True},
        {"name": "Water & Sanitation", "description": "Water and sewage charges", "is_tax_deductible": True},
        {"name": "Electricity", "description": "Electricity charges", "is_tax_deductible": True},
        {"name": "Body Corporate Levy", "description": "Monthly levies paid to body corporate", "is_tax_deductible": True},
        {"name": "Special Levy", "description": "Special levies for improvements or repairs", "is_tax_deductible": True},
        {"name": "Bond Repayment", "description": "Monthly bond/mortgage repayments"},
        {"name": "Bond Interest", "description": "Interest portion of bond payment", "is_tax_deductible": True},
        {"name": "Insurance", "description": "Property and building insurance", "is_tax_deductible": True},
        {"name": "Maintenance", "description": "Regular property maintenance", "is_tax_deductible": True},
        {"name": "Repairs", "description": "Property repairs", "is_tax_deductible": True},
        {"name": "Management Fees", "description": "Property management fees", "is_tax_deductible": True},
        {"name": "Legal Fees", "description": "Legal expenses related to property", "is_tax_deductible": True},
        {"name": "Accounting Fees", "description": "Accounting and tax preparation fees", "is_tax_deductible": True},
        {"name": "Security", "description": "Security services and equipment", "is_tax_deductible": True},
        {"name": "Refuse Removal", "description": "Garbage and waste removal", "is_tax_deductible": True},
        {"name": "Cleaning", "description": "Cleaning services", "is_tax_deductible": True},
        {"name": "Gardening", "description": "Garden and landscaping services", "is_tax_deductible": True},
        {"name": "Pest Control", "description": "Pest control services", "is_tax_deductible": True},
        {"name": "Advertising", "description": "Property advertising and marketing", "is_tax_deductible": True},
        {"name": "Travel", "description": "Travel expenses related to property", "is_tax_deductible": True},
        {"name": "Estate Agent Commission", "description": "Commission paid to rental agents", "is_tax_deductible": True},
        {"name": "Depreciation", "description": "Depreciation of property assets", "is_tax_deductible": True},
    ]
    
    # Create income categories
    for category_data in income_categories:
        FinancialCategory.objects.get_or_create(
            name=category_data["name"],
            company=company,
            category_type=FinancialCategory.TYPE_INCOME,
            defaults={
                "description": category_data["description"],
                "is_default": True
            }
        )
    
    # Create expense categories
    for category_data in expense_categories:
        is_tax_deductible = category_data.get("is_tax_deductible", False)
        FinancialCategory.objects.get_or_create(
            name=category_data["name"],
            company=company,
            category_type=FinancialCategory.TYPE_EXPENSE,
            defaults={
                "description": category_data["description"],
                "is_default": True,
                "is_tax_deductible": is_tax_deductible
            }
        )'weekly':
            return current + timedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return current + timedelta(weeks=2)
        elif self.frequency == 'monthly':
            return current + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            return current + relativedelta(months=3)
        elif self.frequency ==
'''