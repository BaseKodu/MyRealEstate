from django.contrib import admin

# Register your models here.

from .models import User, UserCompanyAccess

admin.site.register(User)
admin.site.register(UserCompanyAccess)
