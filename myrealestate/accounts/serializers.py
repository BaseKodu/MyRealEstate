from rest_framework import serializers
from django.db import transaction
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from .models import User, UserCompanyAccess, UserTypeEnums
from myrealestate.companies.models import Company  # Adjust import path as needed

class CustomRegisterSerializer(RegisterSerializer):
    """Custom registration serializer with company creation"""
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    company_name = serializers.CharField(required=True, max_length=255)
    
    def validate_company_name(self, value):
        """Validate that company name is not"""
        if not value.strip():
            raise serializers.ValidationError("Company name cannot be empty.")
        
        return value.strip()
    
    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'company_name': self.validated_data.get('company_name', ''),
        }
    
    @transaction.atomic
    def save(self, request):
        """Save user and create company with user as company owner"""
        # Create the user first
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.save()
        
        # Create the company
        company_name = self.cleaned_data.get('company_name')
        company = Company.objects.create(
            name=company_name,
        )
        
        # Create UserCompanyAccess with COMPANY_OWNER access level
        UserCompanyAccess.objects.create(
            user=user,
            company=company,
            access_level=UserTypeEnums.COMPANY_OWNER
        )
        
        return user

class UserCompanyAccessSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_id = serializers.IntegerField(source='company.id', read_only=True)
    access_level_display = serializers.CharField(source='get_access_level_display', read_only=True)
    
    class Meta:
        model = UserCompanyAccess
        fields = ['company_id', 'company_name', 'access_level', 'access_level_display', 'created_at']

class CustomUserDetailsSerializer(UserDetailsSerializer):
    """Custom user details serializer"""
    company_accesses = UserCompanyAccessSerializer(source='usercompanyaccess_set', many=True, read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    owned_companies = serializers.SerializerMethodField()
    
    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            'phone_number', 
            'company_accesses', 
            'full_name',
            'owned_companies',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('email', 'created_at', 'updated_at')
    
    def get_owned_companies(self, obj):
        """Get companies where user is the owner"""
        owned_accesses = UserCompanyAccess.objects.filter(
            user=obj, 
            access_level=UserTypeEnums.COMPANY_OWNER
        ).select_related('company')
        
        return [
            {
                'id': access.company.id,
                'name': access.company.name,
                'created_at': access.company.created_at
            }
            for access in owned_accesses
        ]