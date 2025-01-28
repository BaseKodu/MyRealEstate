from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
import uuid
from .models import User
from myrealestate.common.utils import get_email_template
from datetime import datetime
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from .forms import InvitedUserRegistrationForm
from myrealestate.common.views import BaseUpdateView


def send_verification_email(user, request):
    context = {
        'user': user,
        'company_name': user.companies.first().name,
        'verification_url': request.build_absolute_uri(
            reverse('accounts:verify_email', kwargs={'token': user.email_verification_token})
        ),
        'year': datetime.now().year
    }
    
    html_email = get_email_template('emails/verify_email.html', context)
    text_email = get_email_template('emails/verify_email.txt', context)
    
    send_mail(
        'Verify your email address',
        text_email,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_email,
        fail_silently=False
    )

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:verification_sent')

    def form_valid(self, form):
        response = super().form_valid(form)
        send_verification_email(self.object, self.request)
        messages.success(self.request, 'Account created successfully! Please check your email for verification.')
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('home')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)
    
def logout_view(request):
    logout(request)
    return redirect('accounts:login')



class EmailVerificationSentView(TemplateView):
    template_name = 'accounts/verification_sent.html'


class VerifyEmailView(TemplateView):
    template_name = 'accounts/email_verified.html'

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        try:
            user = User.objects.get(email_verification_token=token)
            if not user.email_verified:
                user.email_verified = True
                user.email_verification_token = uuid.uuid4()
                user.save()
                messages.success(request, 'Email verified successfully!')
                return self.render_to_response({})  # Use render_to_response instead of render
            messages.info(request, 'Email already verified. Please login.')
            return redirect('accounts:login')
        except User.DoesNotExist:
            messages.error(request, 'Invalid verification link!')
            print("Invalid verification Link")
            return redirect('accounts:login')          


class EmailVerificationRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.email_verified

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.warning(self.request, 'Please verify your email address to access this page.')
        return redirect('accounts:verification_sent')
    


class CompleteRegistrationView(BaseUpdateView):
    form_class = InvitedUserRegistrationForm
    model = User
    title = "Registration"
    
    def dispatch(self, request, *args, **kwargs):
        # Override dispatch to get user by token instead of pk
        token = self.kwargs.get('token')
        self.object = get_object_or_404(
            User, 
            email_verification_token=token,
            email_verified=False
        )
        return super(BaseUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_invitation'] = True  # Add flag for template
        context['invited_email'] = self.object.email
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.object
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Log the user in after successful completion
        return response

    def get_success_url(self):
        return reverse_lazy('home')  # Or wherever you want to redirect after