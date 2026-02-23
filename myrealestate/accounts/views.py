from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth import get_user_model
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Create your views here.

class CustomConfirmEmailView(APIView):
    """
    Custom view to handle email verification and redirect to frontend
    """

    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        # Get the confirmation key from the URL
        key = kwargs.get('key')
        
        try:
            # Try to confirm the email using the key
            confirmation = EmailConfirmationHMAC.from_key(key)
            if not confirmation:
                # If HMAC verification fails, try the old way
                confirmation = EmailConfirmation.objects.get(key=key)
             
            # Confirm the email
            confirmation.confirm(request)
            
            # Get the frontend URL from settings or use a default
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            
            # Redirect to the frontend with a success parameter
            return redirect(f"{frontend_url}/auth/email-verified?success=true")
            
        except (EmailConfirmation.DoesNotExist, ValueError):
            # Handle the case where the confirmation key is invalid
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/auth/email-verified?success=false")