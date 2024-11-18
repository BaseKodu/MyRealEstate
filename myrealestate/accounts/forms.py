# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User
from django.utils.translation import gettext_lazy as _
from myrealestate.common.forms import BaseModelForm, BaseForm
from myrealestate.companies.models import Company
from .models import UserTypeEnums
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
    
    
    