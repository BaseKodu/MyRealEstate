from rest_framework import permissions
from ..models import UserTypeEnums


class IsCompanyOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is company owner or admin.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superadmin has all permissions
        if request.user.usercompanyaccess_set.filter(
            access_level=UserTypeEnums.SUPERADMIN
        ).exists():
            return True
        
        # Check if user is company owner or admin
        return request.user.usercompanyaccess_set.filter(
            access_level__in=[UserTypeEnums.COMPANY_OWNER, UserTypeEnums.SUBADMIN]
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Superadmin has all permissions
        if request.user.usercompanyaccess_set.filter(
            access_level=UserTypeEnums.SUPERADMIN
        ).exists():
            return True
        
        # For company-related objects, check if user has access to that company
        if hasattr(obj, 'company'):
            return request.user.usercompanyaccess_set.filter(
                company=obj.company,
                access_level__in=[UserTypeEnums.COMPANY_OWNER, UserTypeEnums.SUBADMIN]
            ).exists()
        
        # For user objects, check if user is in the same company
        if hasattr(obj, 'usercompanyaccess_set'):
            user_companies = request.user.usercompanyaccess_set.filter(
                access_level__in=[UserTypeEnums.COMPANY_OWNER, UserTypeEnums.SUBADMIN]
            ).values_list('company_id', flat=True)
            
            return obj.usercompanyaccess_set.filter(
                company_id__in=user_companies
            ).exists()
        
        return False


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission to check if user is superadmin.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.usercompanyaccess_set.filter(
            access_level=UserTypeEnums.SUPERADMIN
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsEmailVerified(permissions.BasePermission):
    """
    Permission to check if user's email is verified.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.email_verified


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class CompanyAccessPermission(permissions.BasePermission):
    """
    Permission to check if user has access to a specific company.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superadmin has access to all companies
        if request.user.usercompanyaccess_set.filter(
            access_level=UserTypeEnums.SUPERADMIN
        ).exists():
            return True
        
        # Check if user has access to the company specified in the request
        company_id = request.data.get('company') or request.query_params.get('company')
        if company_id:
            return request.user.usercompanyaccess_set.filter(
                company_id=company_id
            ).exists()
        
        return True
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Superadmin has access to all companies
        if request.user.usercompanyaccess_set.filter(
            access_level=UserTypeEnums.SUPERADMIN
        ).exists():
            return True
        
        # Check if user has access to the company of the object
        if hasattr(obj, 'company'):
            return request.user.usercompanyaccess_set.filter(
                company=obj.company
            ).exists()
        
        return False 