from django.db import models
from myrealestate.common.models import BaseModel, CurrencyField
from .enums import PropertyType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid
from .enums import TransactionType, PropertyType, PaymentMethod
from . import FinancialCategory, MunicipalAccount, BodyCorporate, PropertyBond


class FinancialTransaction(BaseModel):
    """
    Base model for financial transactions
    """

    
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    
    # Link to property in property hierarchy
    property_type = models.CharField(max_length=2, choices=PropertyType.choices)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="financial_transactions")
    
    # Financial details
    amount = CurrencyField(default=0, help_text="Transaction amount")
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name="transactions")
    
    # VAT information (important for SA businesses)
    includes_vat = models.BooleanField(default=True, help_text="Does this amount include VAT?")
    vat_amount = CurrencyField(default=0, help_text="VAT portion of the amount")
    
    # Transaction metadata
    date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # For expenses
    vendor = models.CharField(max_length=255, blank=True, null=True)
    vendor_vat_number = models.CharField(max_length=20, blank=True, null=True, help_text="VAT registration number of vendor")
    
    # For income - can link to tenant
    tenant = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_transactions")
    
    # Links to specific account types
    municipal_account = models.ForeignKey(MunicipalAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    body_corporate = models.ForeignKey(BodyCorporate, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    property_bond = models.ForeignKey(PropertyBond, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Tax information
    is_tax_deductible = models.BooleanField(default=False, help_text="Is this expense tax deductible?")
    tax_year = models.IntegerField(null=True, blank=True, help_text="Tax year this transaction belongs to")
    
    # Receipt or invoice attachment
    attachment = models.FileField(upload_to='financial/attachments/%Y/%m/', null=True, blank=True)
    
    # Status tracking
    is_paid = models.BooleanField(default=True)
    payment_date = models.DateField(null=True, blank=True, help_text="Date when payment was made or received")
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['property_type', 'property_id']),
            models.Index(fields=['date']),
            models.Index(fields=['is_paid']),
            models.Index(fields=['tax_year']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} on {self.date}"
    
    def clean(self):
        # Ensure category type matches transaction type
        if self.transaction_type == 'income' and self.category.category_type != FinancialCategory.TYPE_INCOME:
            raise ValidationError("Category must be an income category for income transactions")
        if self.transaction_type == 'expense' and self.category.category_type != FinancialCategory.TYPE_EXPENSE:
            raise ValidationError("Category must be an expense category for expense transactions")
        
        # Set tax year if not provided
        if not self.tax_year:
            # South African tax year runs from March to February
            tax_year_start_month = 3  # March
            date_year = self.date.year
            date_month = self.date.month
            
            if date_month < tax_year_start_month:
                self.tax_year = date_year - 1
            else:
                self.tax_year = date_year
    
    def get_property_object(self):
        """Get the actual property object"""
        from myrealestate.properties.models import Estate, Building, Unit
        
        if self.property_type == 'estate':
            return Estate.objects.filter(id=self.property_id).first()
        elif self.property_type == 'building':
            return Building.objects.filter(id=self.property_id).first()
        elif self.property_type == 'unit':
            return Unit.objects.filter(id=self.property_id).first()
        return None
    
    @classmethod
    def get_transactions_for_property(cls, property_obj, start_date=None, end_date=None):
        """
        Get all transactions for a specific property
        """
        property_type = property_obj.__class__.__name__.lower()
        property_id = property_obj.id
        
        query = cls.objects.filter(property_type=property_type, property_id=property_id)
        
        if start_date:
            query = query.filter(date__gte=start_date)
        if end_date:
            query = query.filter(date__lte=end_date)
            
        return query
    
    @classmethod
    def get_income_for_property(cls, property_obj, start_date=None, end_date=None):
        """
        Get income transactions for a specific property
        """
        return cls.get_transactions_for_property(
            property_obj, start_date, end_date
        ).filter(transaction_type='income')
    
    @classmethod
    def get_expenses_for_property(cls, property_obj, start_date=None, end_date=None):
        """
        Get expense transactions for a specific property
        """
        return cls.get_transactions_for_property(
            property_obj, start_date, end_date
        ).filter(transaction_type='expense')
    
    @property
    def is_tax_deductible_auto(self):
        """
        Automatically determine if transaction is tax deductible based on category
        """
        if self.transaction_type == 'expense' and self.category:
            return self.category.is_tax_deductible
        return False