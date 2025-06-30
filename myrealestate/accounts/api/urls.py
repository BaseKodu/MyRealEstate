from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import AuthViewSet, UserViewSet, UserCompanyAccessViewSet
from .viewsets import EmailVerificationView
from .docs import APIDocumentationView

# Create router for ViewSets
router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'company-access', UserCompanyAccessViewSet, basename='company-access')

app_name = 'accounts_api'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Custom API views
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    
    # API Documentation
    path('docs/', APIDocumentationView.as_view(), name='api-docs'),
] 