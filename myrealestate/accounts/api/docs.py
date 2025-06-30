from django.http import JsonResponse
from django.views import View
from django.urls import reverse
from rest_framework.routers import DefaultRouter
from .viewsets import AuthViewSet, UserViewSet, UserCompanyAccessViewSet
from .serializers import (
    UserSerializer, UserDetailSerializer, RegisterSerializer, LoginSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer,
    UserCompanyAccessSerializer, InviteUserSerializer
)


class APIDocumentationView(View):
    """
    Simple API documentation view that returns JSON documentation
    """
    
    def get(self, request):
        # Create router to get URL patterns
        router = DefaultRouter()
        router.register(r'auth', AuthViewSet, basename='auth')
        router.register(r'users', UserViewSet, basename='user')
        router.register(r'company-access', UserCompanyAccessViewSet, basename='company-access')
        
        # Get URL patterns
        url_patterns = []
        for url in router.urls:
            if hasattr(url, 'name') and url.name:
                url_patterns.append({
                    'name': url.name,
                    'pattern': str(url.pattern),
                    'lookup_str': getattr(url, 'lookup_str', ''),
                })
        
        # API Documentation
        api_docs = {
            'title': 'MyRealEstate API Documentation',
            'version': 'v1',
            'base_url': '/api/v1/accounts/',
            'description': 'API for user authentication, management, and company access control',
            'endpoints': {
                'authentication': {
                    'description': 'User authentication endpoints',
                    'endpoints': [
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/auth/register/',
                            'description': 'Register a new user',
                            'required_fields': ['email', 'password', 'password_confirm', 'company_name'],
                            'optional_fields': ['first_name', 'last_name'],
                            'response': {
                                'message': 'Registration successful message',
                                'user_id': 'User ID'
                            }
                        },
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/auth/login/',
                            'description': 'Login user',
                            'required_fields': ['email', 'password'],
                            'response': {
                                'token': 'Authentication token',
                                'user': 'User data',
                                'message': 'Login success message'
                            }
                        },
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/auth/logout/',
                            'description': 'Logout user',
                            'authentication': 'Required',
                            'response': {
                                'message': 'Logout success message'
                            }
                        },
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/auth/password_reset/',
                            'description': 'Request password reset',
                            'required_fields': ['email'],
                            'response': {
                                'message': 'Password reset email sent message'
                            }
                        },
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/auth/password_reset_confirm/',
                            'description': 'Confirm password reset',
                            'required_fields': ['uid', 'token', 'new_password', 'new_password_confirm'],
                            'response': {
                                'message': 'Password reset success message'
                            }
                        }
                    ]
                },
                'users': {
                    'description': 'User management endpoints',
                    'endpoints': [
                        {
                            'method': 'GET',
                            'url': '/api/v1/accounts/users/',
                            'description': 'List users (filtered by permissions)',
                            'authentication': 'Required',
                            'response': 'List of users'
                        },
                        {
                            'method': 'GET',
                            'url': '/api/v1/accounts/users/{id}/',
                            'description': 'Get user details',
                            'authentication': 'Required',
                            'response': 'User details'
                        },
                        {
                            'method': 'GET',
                            'url': '/api/v1/accounts/users/profile/',
                            'description': 'Get current user profile',
                            'authentication': 'Required',
                            'response': 'Current user profile'
                        },
                        {
                            'method': 'PUT/PATCH',
                            'url': '/api/v1/accounts/users/update_profile/',
                            'description': 'Update current user profile',
                            'authentication': 'Required',
                            'fields': ['first_name', 'last_name'],
                            'response': 'Updated user profile'
                        },
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/users/change_password/',
                            'description': 'Change current user password',
                            'authentication': 'Required',
                            'required_fields': ['old_password', 'new_password', 'new_password_confirm'],
                            'response': {
                                'message': 'Password changed successfully'
                            }
                        }
                    ]
                },
                'company_access': {
                    'description': 'User-company access management endpoints',
                    'endpoints': [
                        {
                            'method': 'GET',
                            'url': '/api/v1/accounts/company-access/',
                            'description': 'List company access relationships',
                            'authentication': 'Required',
                            'response': 'List of access relationships'
                        },
                        {
                            'method': 'GET',
                            'url': '/api/v1/accounts/company-access/{id}/',
                            'description': 'Get specific access relationship',
                            'authentication': 'Required',
                            'response': 'Access relationship details'
                        },
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/company-access/invite_user/',
                            'description': 'Invite user to company',
                            'authentication': 'Required',
                            'required_fields': ['email', 'access_level', 'company'],
                            'optional_fields': ['first_name', 'last_name'],
                            'response': {
                                'message': 'User invited successfully',
                                'access': 'Access relationship data'
                            }
                        },
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/company-access/{id}/remove_access/',
                            'description': 'Remove user access to company',
                            'authentication': 'Required',
                            'response': {
                                'message': 'Access removed successfully'
                            }
                        }
                    ]
                },
                'email_verification': {
                    'description': 'Email verification endpoints',
                    'endpoints': [
                        {
                            'method': 'POST',
                            'url': '/api/v1/accounts/verify-email/',
                            'description': 'Resend verification email',
                            'required_fields': ['email'],
                            'response': {
                                'message': 'Verification email sent'
                            }
                        }
                    ]
                }
            },
            'authentication': {
                'methods': [
                    {
                        'type': 'Token Authentication',
                        'header': 'Authorization: Token <your_token>',
                        'description': 'Include token in request headers'
                    },
                    {
                        'type': 'Session Authentication',
                        'description': 'Use Django session cookies (for browser access)'
                    }
                ]
            },
            'permissions': {
                'description': 'API uses role-based permissions',
                'roles': [
                    {
                        'name': 'Superadmin',
                        'description': 'Full access to all data and operations'
                    },
                    {
                        'name': 'Company Owner',
                        'description': 'Full access to company data and user management'
                    },
                    {
                        'name': 'Subadmin',
                        'description': 'Limited admin access to company data'
                    },
                    {
                        'name': 'Company User',
                        'description': 'Basic access to company data'
                    }
                ]
            },
            'error_responses': {
                '400': 'Bad Request - Invalid data provided',
                '401': 'Unauthorized - Authentication required',
                '403': 'Forbidden - Insufficient permissions',
                '404': 'Not Found - Resource not found',
                '500': 'Internal Server Error'
            }
        }
        
        return JsonResponse(api_docs, json_dumps_params={'indent': 2}) 