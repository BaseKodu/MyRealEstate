from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomSignupForm(SignupForm):
    """
    Custom signup form that includes company name and removes username.
    """
    first_name = forms.CharField(
        max_length=30,
        label=_('First Name'),
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Last Name'),
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name'
        })
    )
    company_name = forms.CharField(
        max_length=255,
        label=_('Company Name'),
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your company name',
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field
        if 'username' in self.fields:
            del self.fields['username']
        
        # Make email field required and add placeholder
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
        
        # Update password fields
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    
    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class CustomLoginForm(LoginForm):
    """
    Custom login form that uses email instead of username.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change username field to email
        self.fields['login'].label = _('Email')
        self.fields['login'].widget.attrs.update({
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    
    def clean_login(self):
        email = self.cleaned_data['login']
        return email


class CustomPasswordResetForm(forms.Form):
    """
    Custom password reset form.
    """
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('No user found with this email address.'))
        return email


class CustomSetPasswordForm(forms.Form):
    """
    Custom set password form.
    """
    new_password1 = forms.CharField(
        label=_('New Password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_('Confirm New Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        }),
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return password2
    
    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user 