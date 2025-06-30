from django.db import models
from django.utils.translation import gettext_lazy as _
from myrealestate.common.models import BaseModel


class Company(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Company Name"))
    # Business Information
    trading_name = models.CharField(_('Trading Name'), max_length=255, blank=True)
    registration_number = models.CharField(_('Registration Number'), max_length=100, blank=True)
    tax_number = models.CharField(_('Tax/VAT Number'), max_length=100, blank=True)
    
    # Contact Details
    business_email = models.EmailField(_('Business Email'), blank=True)
    support_email = models.EmailField(_('Support Email'), blank=True)
    accounts_email = models.EmailField(_('Accounts Email'), blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    website = models.URLField(_('Website'), blank=True)

    
    class Meta:
        verbose_name = _('Company Settings')
        verbose_name_plural = _('Company Settings')

    def __str__(self):
        return f"{self.company.name} Settings"
    
    def __str__(self):
        return self.name
