from django import forms
from django.urls import reverse
from .models import Company
from myrealestate.common.forms import BaseModelForm
from myrealestate.accounts.models import UserTypeEnums, User, UserCompanyAccess
from django.utils.translation import gettext_lazy as _
import uuid
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


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

class UserInvitationForm(BaseModelForm):
    email = forms.EmailField(
        label=_("User's Email"),
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email address'})
    )
    
    access_level = forms.ChoiceField(
        choices=[
            (UserTypeEnums.COMPANY_USER, 'Company User'),
            (UserTypeEnums.TENANT, 'Tenant'),
            (UserTypeEnums.BUYER, 'Buyer')
        ],
        label=_("Access Level")
    )


    def __init__(self, *args, **kwargs):
        self.inviter = kwargs.pop('inviter', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    class Meta:
        model = UserCompanyAccess
        fields = ['email', 'access_level']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        access_level = cleaned_data.get('access_level')

        # Check if inviter has permission to add users
        if not self.inviter.usercompanyaccess_set.filter(
            company=self.company, 
            access_level=UserTypeEnums.COMPANY_OWNER
        ).exists():
            raise forms.ValidationError(_("You don't have permission to add users."))

        # Check if user is already a member of this company
        if UserCompanyAccess.objects.filter(
            user__email=email,
            company=self.company
        ).exists():
            raise forms.ValidationError(_("This user already has access to this company."))

        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data['email']
        access_level = self.cleaned_data['access_level']
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email, 
                'email_verified': False,
                'email_verification_token': uuid.uuid4()
            }
        )
        
        if created:
            # Send verification email for new users
            user.generate_verification_token()
        
        # Create company access
        instance = UserCompanyAccess(
            user=user,
            company=self.company,
            access_level=access_level
        )
        
        if commit:
            instance.save()
            # Send invitation email
            self.send_invitation_email(user)
            
        return instance

    def send_invitation_email(self, user):
        verification_url = reverse('accounts:complete_registration', 
                                 kwargs={'token': user.email_verification_token})
        absolute_url = self.request.build_absolute_uri(verification_url)
        
        context = {
            'verification_url': absolute_url,
            'company_name': self.company.name,
            'inviter_email': self.inviter.email
        }
        
        send_mail(
            subject=f'Invitation to join {self.company.name}',
            message=render_to_string('emails/invitation_email.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=render_to_string('emails/invitation_email.html', context)
        )


class UserCompanyAccessForm(BaseModelForm):
    class Meta:
        model = UserCompanyAccess
        fields = ['access_level']
        