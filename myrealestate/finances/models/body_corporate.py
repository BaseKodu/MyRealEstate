from django.db import models
from myrealestate.common.models import BaseModel, CurrencyField
from django.core.validators import MinValueValidator
from .enums import PropertyType
from django.utils.translation import gettext_lazy as _
from .enums import PropertyType





class BodyCorporate(BaseModel):
    """
    Tracks body corporate (HOA) details for sectional title properties
    """
    
    property_type = models.CharField(max_length=2, choices=PropertyType.choices)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="body_corporates")
    
    # Body corporate details
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Levy details
    monthly_levy = CurrencyField(help_text="Regular monthly levy amount")
    special_levy = CurrencyField(default=0, help_text="Any special levy currently in effect")
    special_levy_end_date = models.DateField(null=True, blank=True)
    levy_increase_month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)], default=1, help_text="Month when levies typically increase")
    
    # Payment details
    payment_day = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Day of month when payment is due")
    account_number = models.CharField(max_length=100, blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Body corporates"
        
    def __str__(self):
        return f"Body Corporate: {self.name}"
    
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
