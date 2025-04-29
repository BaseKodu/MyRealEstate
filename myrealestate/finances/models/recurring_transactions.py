from django.db import models
from myrealestate.common.models import BaseModel, CurrencyField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid
from .enums import RecurrenceFrequency, PropertyType, TransactionType, CategoryType
from . import FinancialCategory, MunicipalAccount, BodyCorporate, PropertyBond, FinancialTransaction


class RecurringTransaction(BaseModel):
    """
    Template for recurring financial transactions
    """
    
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    
    # Link to property
    property_type = models.CharField(max_length=2, choices=PropertyType.choices)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="recurring_transactions")
    
    # Financial details
    amount = CurrencyField(help_text="Amount")
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name="recurring_transactions")
    
    # VAT information
    includes_vat = models.BooleanField(default=True, help_text="Does this amount include VAT?")
    vat_amount = CurrencyField(default=0, help_text="VAT portion of the amount")
    
    # Recurrence details
    frequency = models.CharField(max_length=15, choices=RecurrenceFrequency.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField()
    
    # For expenses
    vendor = models.CharField(max_length=255, blank=True, null=True)
    vendor_vat_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Links to specific account types
    municipal_account = models.ForeignKey(MunicipalAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="recurring_transactions")
    body_corporate = models.ForeignKey(BodyCorporate, on_delete=models.SET_NULL, null=True, blank=True, related_name="recurring_transactions")
    property_bond = models.ForeignKey(PropertyBond, on_delete=models.SET_NULL, null=True, blank=True, related_name="recurring_transactions")
    
    # For tenant-related transactions
    tenant = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name="tenant_recurring_transactions")
    
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Tax information
    is_tax_deductible = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['next_due_date']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} ({self.get_frequency_display()})"
    
    def clean(self):
        # Ensure category type matches transaction type
        if self.transaction_type == 'income' and self.category.category_type != CategoryType.INCOME:
            raise ValidationError("Category must be an income category for income transactions")
        if self.transaction_type == 'expense' and self.category.category_type != CategoryType.EXPENSE:
            raise ValidationError("Category must be an expense category for expense transactions")
    
    def calculate_next_due_date(self):
        """
        Calculate the next due date based on frequency and current next_due_date
        """
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        current = self.next_due_date
        
        if self.frequency == 'daily':
            return current + timedelta(days=1)
        elif self.frequency == 'semiannually':
            return current + relativedelta(months=6)
        elif self.frequency == 'annually':
            return current + relativedelta(years=1)
        return current
    
    def create_transaction(self):
        """
        Create a financial transaction based on this recurring template
        """
        # Determine tax year
        tax_year_start_month = 3  # March
        date_year = self.next_due_date.year
        date_month = self.next_due_date.month
        
        if date_month < tax_year_start_month:
            tax_year = date_year - 1
        else:
            tax_year = date_year
        
        transaction = FinancialTransaction(
            transaction_type=self.transaction_type,
            property_type=self.property_type,
            property_id=self.property_id,
            company=self.company,
            amount=self.amount,
            category=self.category,
            date=self.next_due_date,
            tenant=self.tenant,
            vendor=self.vendor,
            vendor_vat_number=self.vendor_vat_number,
            includes_vat=self.includes_vat,
            vat_amount=self.vat_amount,
            is_tax_deductible=self.is_tax_deductible,
            tax_year=tax_year,
            municipal_account=self.municipal_account,
            body_corporate=self.body_corporate,
            property_bond=self.property_bond,
            description=self.description,
            notes=f"Auto-generated from recurring transaction: {self.pk}"
        )
        transaction.save()
        
        # Update next due date
        self.next_due_date = self.calculate_next_due_date()
        
        # If end date is set and we've passed it, deactivate
        if self.end_date and self.next_due_date > self.end_date:
            self.is_active = False
            
        self.save()
        
        return transaction