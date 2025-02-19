from django.db import models
from django.utils.translation import gettext_lazy as _
from myrealestate.common.models import BaseModel
# Create your models here.


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

    # Financial Settings
    #currency = models.CharField(_('Default Currency'), max_length=3, default='ZAR')
    #payment_terms = models.PositiveIntegerField(_('Default Payment Terms (days)'), default=30)
    #late_fee_percentage = models.DecimalField(
    #    _('Late Fee Percentage'),
    #    max_digits=5,
    #    decimal_places=2,
    #    default=0
    #)
    
    # Property Management Settings
    '''
    inspection_frequency = models.PositiveIntegerField(
        _('Inspection Frequency (months)'),
        default=6,
        help_text=_('How often properties should be inspected')
    )
    maintenance_threshold = models.DecimalField(
        _('Maintenance Approval Threshold'),
        max_digits=10,
        decimal_places=2,
        default=1000,
        help_text=_('Amount above which maintenance requires approval')
    )

    # Document Settings
    lease_template = models.FileField(
        _('Default Lease Template'),
        upload_to='company_templates/leases/',
        null=True,
        blank=True
    )
    inspection_template = models.FileField(
        _('Default Inspection Template'),
        upload_to='company_templates/inspections/',
        null=True,
        blank=True
    )

    # Notification Settings
    notify_on_maintenance = models.BooleanField(
        _('Notify on Maintenance Requests'),
        default=True
    )
    notify_on_lease_expiry = models.BooleanField(
        _('Notify on Lease Expiry'),
        default=True
    )
    lease_expiry_notice_days = models.PositiveIntegerField(
        _('Lease Expiry Notice Days'),
        default=60,
        help_text=_('Days before lease expiry to send notification')
    )
    rent_reminder_days = models.PositiveIntegerField(
        _('Rent Reminder Days'),
        default=5,
        help_text=_('Days before rent due to send reminder')
    )
    '''

    # Branding Settings
    #logo = models.ImageField(
    #    _('Company Logo'),
    #    upload_to='company_logos/',
    #    null=True,
    #    blank=True
    #)
    '''
    primary_color = models.CharField(
        _('Primary Color'),
        max_length=7,
        default='#4338CA',
        help_text=_('Primary brand color in hex format')
    )
    '''
    
    # System Settings
    '''
    enable_tenant_portal = models.BooleanField(
        _('Enable Tenant Portal'),
        default=True
    )
    enable_owner_portal = models.BooleanField(
        _('Enable Owner Portal'),
        default=True
    )
    enable_maintenance_portal = models.BooleanField(
        _('Enable Maintenance Portal'),
        default=True
    )
    '''

    class Meta:
        verbose_name = _('Company Settings')
        verbose_name_plural = _('Company Settings')

    def __str__(self):
        return f"{self.company.name} Settings"
    
    def __str__(self):
        return self.name
