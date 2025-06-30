from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ..models import User, UserCompanyAccess, UserTypeEnums
from myrealestate.companies.models import Company
from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer
from allauth.account.adapter import get_adapter


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for read operations"""
    companies = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'email_verified', 'companies', 'date_joined']
        read_only_fields = ['id', 'email_verified', 'date_joined']
    
    def get_companies(self, obj):
        return [
            {
                'id': access.company.id,
                'name': access.company.name,
                'access_level': access.access_level,
                'access_level_display': access.get_access_level_display()
            }
            for access in obj.usercompanyaccess_set.select_related('company').all()
        ]


class UserDetailSerializer(UserSerializer):
    """Detailed user serializer with more fields"""
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['is_active', 'last_login']


class CustomRegisterSerializer(DefaultRegisterSerializer):
    username = None  # Remove username field
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    company_name = serializers.CharField(required=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'company_name': self.validated_data.get('company_name', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        
        # Set user fields
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email_verified = False
        
        # Set password
        adapter.save_user(request, user, self)
        
        # Create company and assign user as owner
        company = Company.objects.create(name=self.cleaned_data.get('company_name'))
        UserCompanyAccess.objects.create(
            user=user,
            company=company,
            access_level=UserTypeEnums.COMPANY_OWNER
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError(_('Invalid email or password.'))
            if not user.is_active:
                raise serializers.ValidationError(_('User account is disabled.'))
            attrs['user'] = user
        else:
            raise serializers.ValidationError(_('Must include "email" and "password".'))
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Old password is incorrect.'))
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("New passwords don't match."))
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('No user found with this email address.'))
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("Passwords don't match."))
        return attrs


class UserCompanyAccessSerializer(serializers.ModelSerializer):
    """Serializer for user-company access relationships"""
    user = UserSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    access_level_display = serializers.CharField(source='get_access_level_display', read_only=True)
    
    class Meta:
        model = UserCompanyAccess
        fields = ['id', 'user', 'company', 'company_name', 'access_level', 'access_level_display', 'created_at']
        read_only_fields = ['id', 'created_at']


class InviteUserSerializer(serializers.Serializer):
    """Serializer for inviting users to companies"""
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    access_level = serializers.ChoiceField(choices=UserTypeEnums.choices)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    
    def validate_email(self, value):
        # Check if user already has access to this company
        company = self.initial_data.get('company')
        if company:
            existing_access = UserCompanyAccess.objects.filter(
                user__email=value, 
                company=company
            ).exists()
            if existing_access:
                raise serializers.ValidationError(_('User already has access to this company.'))
        return value 


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to add extra claims"""
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['email'] = user.email
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['email_verified'] = user.email_verified
        return data


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """Custom user details serializer for dj-rest-auth"""
    companies = serializers.SerializerMethodField()
    email_verified = serializers.BooleanField(read_only=True)
    
    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('email_verified', 'companies',)
    
    def get_companies(self, obj):
        return [
            {
                'id': access.company.id,
                'name': access.company.name,
                'access_level': access.access_level,
                'access_level_display': access.get_access_level_display()
            }
            for access in obj.usercompanyaccess_set.select_related('company').all()
        ] 