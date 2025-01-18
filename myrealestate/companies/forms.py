from django import forms
from .models import Company
from myrealestate.common.forms import BaseModelForm


class CompanySettingsForm(BaseModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'trading_name', 'registration_number', 'tax_number',
            'business_email', 'support_email', 'accounts_email', 'phone', 'website'
        ]

    use_email_for_comm = forms.BooleanField(required=False, label='Use this Email for Communication')
    cc_email = forms.EmailField(required=False, label='CC Email')
    always_cc = forms.BooleanField(required=False, label='Always CC this Email Address')

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        self.instance = company if company else self.instance
        
        # Group fields for template organization
        self.fieldsets = {
            'company_details': {
                'title': 'Company Details',
                'fields': ['name', 'trading_name', 'registration_number', 'tax_number']
            },
            'commmunication': {
                'title': 'Communication',
                'fields': ['business_email', 'support_email', 'accounts_email', 'phone', 'website']
            }
        }

    def clean(self):
        cleaned_data = super().clean()
        # Add any cross-field validation here
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
