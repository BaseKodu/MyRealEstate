from django.db import models
from django.utils.translation import gettext_lazy as _
from myrealestate.common.models import BaseModel

# Create your models here.


class Company(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Company Name"))
    contact_email = models.EmailField(verbose_name=_("Contact Email"))
    contact_phone = models.CharField(max_length=20, verbose_name=_("Contact Phone"))
    #address = models.TextField(verbose_name=_("Address"))
    # Add these fields
    #registration_number = models.CharField(max_length=100, blank=True, verbose_name=_("Registration Number"))
    #tax_number = models.CharField(max_length=100, blank=True, verbose_name=_("Tax Number"))
    #logo = models.ImageField(upload_to='company_logos/', null=True, blank=True, verbose_name=_("Logo"))
    
    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    
    def __str__(self):
        return self.name