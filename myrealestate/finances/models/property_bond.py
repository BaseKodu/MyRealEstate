from django.db import models
from myrealestate.common.models import BaseModel, CurrencyField
from .enums import InterestRateType
from . import PropertyPurchase
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _




class PropertyBond(BaseModel):
    """
    Tracks mortgage/bond details for a property
    """
    property_purchase = models.ForeignKey(PropertyPurchase, on_delete=models.CASCADE, related_name="bonds")
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="property_bonds")
    
    # Basic bond information
    lender = models.CharField(max_length=255, help_text=_("Bank or financial institution"))
    account_number = models.CharField(max_length=100, blank=True, null=True)
    bond_amount = CurrencyField(help_text=_("Total bond amount"))
    start_date = models.DateField()
    term_years = models.PositiveIntegerField(help_text=_("Bond term in years"))
    
    # Interest rate details
    interest_rate_type = models.CharField(max_length=2, choices=InterestRateType.choices, default=InterestRateType.VARIABLE)
    current_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Current annual interest rate (%)"), validators=[MinValueValidator(0)])
    prime_linked = models.BooleanField(default=True, help_text=_("Is rate linked to prime rate?"))
    prime_rate_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text=_("Margin above/below prime rate (%)"))
    
    # Payment details
    monthly_payment = CurrencyField(help_text=_("Regular monthly bond payment"))
    payment_day = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text=_("Day of month when payment is due"))
    
    # Additional bond information
    is_active = models.BooleanField(default=True)
    initiation_fee = CurrencyField(default=0)
    has_payment_holiday = models.BooleanField(default=False)
    payment_holiday_end_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Bond for {self.property_purchase}: {self.bond_amount} ({self.lender})"
    
    @property
    def end_date(self):
        """Calculate the end date based on start date and term"""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        return self.start_date + relativedelta(years=self.term_years)
    
    @property
    def remaining_term_months(self):
        """Calculate remaining term in months"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        if not self.is_active:
            return 0
            
        today = date.today()
        end_date = self.end_date
        
        if today >= end_date:
            return 0
            
        diff = relativedelta(end_date, today)
        return diff.years * 12 + diff.months