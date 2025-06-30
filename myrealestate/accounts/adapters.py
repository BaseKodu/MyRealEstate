from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import TemplateDoesNotExist
from django.utils.translation import gettext_lazy as _
from .models import UserTypeEnums
from myrealestate.companies.models import Company

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for django-allauth to handle email-only authentication
    and integrate with our company creation logic.
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to set the data properly.
        """
        data = form.cleaned_data
        email = data.get('email')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        password1 = data.get('password1')
        
        user_email(user, email)
        user_field(user, 'first_name', first_name)
        user_field(user, 'last_name', last_name)
        
        if password1:
            user.set_password(password1)
        
        # Set email_verified to False initially
        user.email_verified = False
        
        if commit:
            user.save()
            
            # Create company if company_name is provided
            company_name = data.get('company_name')
            if company_name:
                company = Company.objects.create(name=company_name)
                user.companies.add(company, through_defaults={'access_level': UserTypeEnums.COMPANY_OWNER})
        
        return user
    
    def is_open_for_signup(self, request):
        """
        Whether to allow sign ups.
        """
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)
    
    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Returns the URL for email confirmation.
        """
        # Use our custom verification URL
        return f"{settings.FRONTEND_URL}/verify-email/{emailconfirmation.key}/"
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send the confirmation email.
        """
        current_site = getattr(request, 'site', None)
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
        }
        
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)
    
    def send_mail(self, template_prefix, email, context):
        """
        Send an email to the user.
        """
        msg = self.render_mail(template_prefix, email, context)
        msg.send()
    
    def render_mail(self, template_prefix, email, context):
        """
        Renders an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        subject = self.render_mail_template(template_prefix, "subject", context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)
        
        from_email = self.get_from_email()
        
        bodies = {}
        for ext in ['html', 'txt']:
            try:
                template_name = "{0}_message.{1}".format(template_prefix, ext)
                bodies[ext] = self.render_mail_template(template_prefix,
                                                       "message", context).strip()
            except TemplateDoesNotExist:
                if ext == 'txt' and not bodies:
                    # We need at least one body
                    from django.template.loader import render_to_string
                    template_name = "{0}_message.txt".format(template_prefix)
                    bodies['txt'] = render_to_string(template_name, context).strip()
                else:
                    continue
        
        if "txt" in bodies:
            msg = EmailMultiAlternatives(subject, bodies["txt"], from_email, [email])
            if "html" in bodies:
                msg.attach_alternative(bodies["html"], 'text/html')
        else:
            msg = EmailMessage(subject, bodies["html"], from_email, [email])
            msg.content_subtype = 'html'  # Main content is now text/html
        
        return msg


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social authentication.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed.
        """
        pass
    
    def populate_user(self, request, sociallogin, data):
        """
        Populates user data from social provider data.
        """
        user = sociallogin.user
        if user:
            user.email = data.get('email', '')
            user.first_name = data.get('first_name', '')
            user.last_name = data.get('last_name', '')
            user.email_verified = True  # Social accounts are pre-verified
        return user 