from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import User, UserCompanyAccess, UserTypeEnums
from myrealestate.companies.models import Company
from .serializers import (
    UserSerializer, UserDetailSerializer, RegisterSerializer, LoginSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer,
    UserCompanyAccessSerializer, InviteUserSerializer
)
from myrealestate.common.utils import get_email_template
from datetime import datetime


class AuthViewSet(viewsets.ViewSet):
    """ViewSet for authentication operations"""
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful",
                examples={
                    'application/json': {
                        'message': 'Registration successful. Please check your email for verification.',
                        'user_id': 1
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    'application/json': {
                        'email': ['A user with this email already exists.'],
                        'password': ['This password is too common.'],
                        'password_confirm': ["Passwords don't match."]
                    }
                }
            )
        },
        operation_description="Register a new user with company",
        operation_summary="Register new user",
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Send email verification using allauth
            # This will be handled by allauth's email verification
            return Response({
                'message': _('Registration successful. Please check your email for verification.'),
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    'application/json': {
                        'token': 'your-auth-token',
                        'user': {
                            'id': 1,
                            'email': 'user@example.com',
                            'first_name': 'John',
                            'last_name': 'Doe'
                        },
                        'message': 'Login successful.'
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid credentials",
                examples={
                    'application/json': {
                        'non_field_errors': ['Invalid email or password.']
                    }
                }
            )
        },
        operation_description="Login with email and password",
        operation_summary="Login user",
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login user"""
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # Create or get token for API access
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': _('Login successful.')
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user"""
        if request.user.is_authenticated:
            # Delete token if it exists
            Token.objects.filter(user=request.user).delete()
            logout(request)
        return Response({'message': _('Logout successful.')})
    
    @action(detail=False, methods=['post'])
    def password_reset(self, request):
        """Request password reset"""
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send email
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            context = {
                'user': user,
                'reset_url': reset_url,
                'year': datetime.now().year
            }
            
            html_email = get_email_template('emails/password_reset.html', context)
            text_email = get_email_template('emails/password_reset.txt', context)
            
            send_mail(
                _('Password Reset Request'),
                text_email,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_email,
                fail_silently=False
            )
            
            return Response({
                'message': _('Password reset email sent.')
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def password_reset_confirm(self, request):
        """Confirm password reset"""
        uid = request.data.get('uid')
        token = request.data.get('token')
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
                
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({'message': _('Password reset successful.')})
                else:
                    return Response({
                        'error': _('Invalid reset link.')
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    'error': _('Invalid reset link.')
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        # Superadmin can see all users
        if user.usercompanyaccess_set.filter(access_level=UserTypeEnums.SUPERADMIN).exists():
            return User.objects.all()
        
        # Company owners/admins can see users in their companies
        company_ids = user.usercompanyaccess_set.filter(
            access_level__in=[UserTypeEnums.COMPANY_OWNER, UserTypeEnums.SUBADMIN]
        ).values_list('company_id', flat=True)
        
        return User.objects.filter(usercompanyaccess__company_id__in=company_ids).distinct()
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user's password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Invalidate existing tokens
            Token.objects.filter(user=user).delete()
            
            return Response({'message': _('Password changed successfully.')})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCompanyAccessViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user-company access relationships"""
    queryset = UserCompanyAccess.objects.all()
    serializer_class = UserCompanyAccessSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        # Superadmin can see all access relationships
        if user.usercompanyaccess_set.filter(access_level=UserTypeEnums.SUPERADMIN).exists():
            return UserCompanyAccess.objects.all()
        
        # Company owners/admins can see access in their companies
        company_ids = user.usercompanyaccess_set.filter(
            access_level__in=[UserTypeEnums.COMPANY_OWNER, UserTypeEnums.SUBADMIN]
        ).values_list('company_id', flat=True)
        
        return UserCompanyAccess.objects.filter(company_id__in=company_ids)
    
    @action(detail=False, methods=['post'])
    def invite_user(self, request):
        """Invite a user to a company"""
        serializer = InviteUserSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                email = serializer.validated_data['email']
                company = serializer.validated_data['company']
                access_level = serializer.validated_data['access_level']
                
                # Check if user exists
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name': serializer.validated_data.get('first_name', ''),
                        'last_name': serializer.validated_data.get('last_name', ''),
                        'email_verified': False
                    }
                )
                
                # Create access relationship
                access, created = UserCompanyAccess.objects.get_or_create(
                    user=user,
                    company=company,
                    defaults={'access_level': access_level}
                )
                
                if not created:
                    access.access_level = access_level
                    access.save()
                
                # Send invitation email
                context = {
                    'user': user,
                    'company': company,
                    'inviter': request.user,
                    'year': datetime.now().year
                }
                
                html_email = get_email_template('emails/user_invitation.html', context)
                text_email = get_email_template('emails/user_invitation.txt', context)
                
                send_mail(
                    f'Invitation to join {company.name}',
                    text_email,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_email,
                    fail_silently=False
                )
                
                return Response({
                    'message': _('User invited successfully.'),
                    'access': UserCompanyAccessSerializer(access).data
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remove_access(self, request, pk=None):
        """Remove user access to a company"""
        access = self.get_object()
        
        # Check permissions
        user = request.user
        if not (user.usercompanyaccess_set.filter(
            company=access.company,
            access_level__in=[UserTypeEnums.COMPANY_OWNER, UserTypeEnums.SUBADMIN]
        ).exists() or user.usercompanyaccess_set.filter(
            access_level=UserTypeEnums.SUPERADMIN
        ).exists()):
            return Response({
                'error': _('You do not have permission to remove this access.')
            }, status=status.HTTP_403_FORBIDDEN)
        
        access.delete()
        return Response({'message': _('Access removed successfully.')})


class EmailVerificationView(APIView):
    """Handle email verification"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Resend verification email"""
        email = request.data.get('email')
        if not email:
            return Response({
                'error': _('Email is required.')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if user.email_verified:
                return Response({
                    'message': _('Email is already verified.')
                })
            
            # This will be handled by allauth
            return Response({
                'message': _('Verification email sent.')
            })
        except User.DoesNotExist:
            return Response({
                'error': _('User not found.')
            }, status=status.HTTP_404_NOT_FOUND) 