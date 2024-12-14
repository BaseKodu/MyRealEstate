from django.urls import path
from .views import RegisterView, CustomLoginView, logout_view, EmailVerificationSentView, VerifyEmailView


app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('verification-sent/', EmailVerificationSentView.as_view(), name='verification_sent'),
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify_email'),
]
