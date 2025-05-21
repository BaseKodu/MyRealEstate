# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from myrealestate.common.forms import BaseModelForm, BaseForm
from .models import User, UserTypeEnums
import uuid
from myrealestate.companies.models import Company


class CustomUserCreationForm(BaseModelForm, UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'autocomplete': 'email'
        })
    )
    
    username = forms.CharField(
        label=_("Username"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        })
    )
    
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    )
    
    company_name = forms.CharField(
        label=_("Company Name"),
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your company name',
        })
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("This email is already registered."))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("This username is already taken."))
        return username
    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            company_name = self.cleaned_data['company_name']
            company = Company.objects.create(
                name=company_name,
            )
            user.companies.add(company, through_defaults={'access_level': UserTypeEnums.COMPANY_OWNER})
            user.email_verified = False
            user.email_verification_token = uuid.uuid4()
        return user

class CustomAuthenticationForm(BaseForm, AuthenticationForm):
    username = forms.CharField(
        label=_("Email or Username"),
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your email or username',
            'autocomplete': 'username'
        })
    )
    
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct email/username and password."
        ),
        'inactive': _("This account is inactive."),
    }
    

class InvitedUserRegistrationForm(CustomUserCreationForm):
    # Remove email field since it's already set
    email = None
    # Remove company_name field since they're being invited to an existing company
    company_name = None

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, user=None, *args, **kwargs):
        self.invited_user = user
        super().__init__(*args, **kwargs)
        # Remove email field from the form
        if 'email' in self.fields:
            del self.fields['email']

    def save(self, commit=True):
        if not self.invited_user:
            raise ValueError("Invited user instance is required")
        
        self.invited_user.username = self.cleaned_data['username']
        self.invited_user.set_password(self.cleaned_data['password1'])
        self.invited_user.email_verified = True
        self.invited_user.email_verification_token = None
        
        if commit:
            self.invited_user.save()
        
        return self.invited_user