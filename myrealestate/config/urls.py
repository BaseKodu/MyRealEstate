"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myrealestate.companies.views import home
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="MyRealEstate API",
        default_version='v1',
        description="API documentation for MyRealEstate application",
        terms_of_service="https://www.myrealestate.com/terms/",
        contact=openapi.Contact(email="contact@myrealestate.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myrealestate.accounts.urls', namespace='accounts')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('home/', home, name='home'),
    path('properties/', include('myrealestate.properties.urls', namespace='properties')),
    path('company/', include('myrealestate.companies.urls', namespace='companies')),
    
    # API URLs
    path('api/v1/accounts/', include('myrealestate.accounts.api.urls', namespace='accounts_api')),
    
    # JWT Authentication URLs
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # API Documentation
    path('api/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]