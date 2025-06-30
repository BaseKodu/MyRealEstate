from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserCompanyAccess

class UserCompanyAccessInline(admin.TabularInline):
    model = UserCompanyAccess
    extra = 1

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = [UserCompanyAccessInline]

@admin.register(UserCompanyAccess)
class UserCompanyAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'access_level', 'created_at')
    list_filter = ('access_level', 'created_at')
    search_fields = ('user__email', 'company__name')