from django.db import models
from myrealestate.common.models import BaseModel, MoneyField
from django.core.validators import MinValueValidator
from .enums import PropertyType
from django.utils.translation import gettext_lazy as _

class MunicipalAccount(BaseModel):
    """
    Tracks municipal account details for a property
    """
    
    property_type = models.CharField(max_length=2, choices=PropertyType.choices)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="municipal_accounts")
    
    # Municipal account details
    municipality = models.CharField(max_length=255, help_text=_("Name of municipality"))
    account_number = models.CharField(max_length=100)
    account_holder = models.CharField(max_length=255)
    
    # Service details
    includes_water = models.BooleanField(default=True)
    includes_electricity = models.BooleanField(default=True)
    includes_sewage = models.BooleanField(default=True)
    includes_refuse = models.BooleanField(default=True)
    includes_rates = models.BooleanField(default=True)
    
    # Billing details
    billing_day = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text=_("Day of month when bill is typically issued"))
    payment_day = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text=_("Day of month when payment is due"))
    
    # Property valuation for rates
    municipal_valuation = MoneyField(null=True, blank=True, help_text=_("Municipal valuation for rates calculation"))
    valuation_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['municipality', 'account_number']
        
    def __str__(self):
        return f"Municipal Account: {self.account_number} ({self.municipality})"
    
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