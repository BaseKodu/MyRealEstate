from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm

# Create your views here.
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please login.')
        return response
    
    def form_invalid(self, form):
        for field in form.errors:
            for error in form.errors[field]:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)