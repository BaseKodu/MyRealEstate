from django.urls import path, include
from .views import CompanySettingsView, CompanyUsersView, InviteUserView, CheckEmailView, UserCompanyAccessUpdateView, UserCompanyAccessDeleteView
from myrealestate.accounts.views import CompleteRegistrationView


app_name="companies"

urlpatterns = [
    path("", CompanySettingsView.as_view(), name="home"),
    path('users/', CompanyUsersView.as_view(), name='company_users'),
    path('users/invite/', InviteUserView.as_view(), name='invite_user'),
    path('users/<int:pk>/update/', UserCompanyAccessUpdateView.as_view(), name='update-usercompanyaccess'),
    path('users/<int:pk>/delete/', UserCompanyAccessDeleteView.as_view(), name='delete-usercompanyaccess'),
    
    # API endpoints
    path('api/users/check-email/', CheckEmailView.as_view(), name='check_user_email'),
]

'''
# urls.py
urlpatterns = [
    path('users/', CompanyUsersView.as_view(), name='company_users'),
    path('users/invite/', InviteUserView.as_view(), name='invite_user'),
    path('api/users/check-email/', CheckEmailView.as_view(), name='check_user_email'),
    #path('register/complete/<uuid:token>/', CompleteRegistrationView.as_view(), name='complete_registration'),
]
'''