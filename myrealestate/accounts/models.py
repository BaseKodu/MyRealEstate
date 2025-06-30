from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class UserTypeEnums(models.TextChoices):
    SUPERADMIN = 'sa', _('Superadmin')
    SUBADMIN = 'su', _('Subadmin')
    COMPANY_OWNER = 'co', _('Company Owner')
    COMPANY_USER = 'cu', _('Company User')
    TENANT = 'te', _('Tenant')
    BUYER = 'bu', _('Buyer')

class User(AbstractUser):
    # Remove username field requirement
    username = None
    
    # Make email the unique identifier
    email = models.EmailField(_('email address'), unique=True)
    
    # Add your custom fields
    companies = models.ManyToManyField(
        'companies.Company',
        through='UserCompanyAccess',
        through_fields=('user', 'company'),
        related_name='users',
        verbose_name=_('Companies'),
        blank=True
    )
    
    # Additional custom fields you might need
    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove email from required fields since it's the username field
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return self.email
    
    
    def has_company_access(self, company, access_level=None):
        """Check if user has access to a specific company"""
        query = UserCompanyAccess.objects.filter(user=self, company=company)
        if access_level:
            query = query.filter(access_level=access_level)
        return query.exists()
    
    def is_superadmin(self):
        """Check if user is a superadmin"""
        return UserCompanyAccess.objects.filter(
            user=self, 
            access_level=UserTypeEnums.SUPERADMIN
        ).exists()

class UserCompanyAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    access_level = models.CharField(max_length=2, choices=UserTypeEnums.choices)
    
    # Add timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'company')  # One access level per company
        verbose_name = _('User Company Access')
        verbose_name_plural = _('User Company Accesses')
    
    def __str__(self):
        return f"{self.user.email} - {self.company.name} - {self.get_access_level_display()}"
    
    def clean(self):
        if self.access_level in [UserTypeEnums.SUPERADMIN, UserTypeEnums.SUBADMIN]:
            raise ValidationError("Superadmin and Subadmin cannot be assigned to any company.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)