from django.urls import path, include
from .views import CompanySettingsView


app_name="companies"

urlpatterns = [
    path("", CompanySettingsView.as_view(), name="home")
]