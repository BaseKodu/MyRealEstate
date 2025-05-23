import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from myrealestate.companies.models import Company
from myrealestate.common.models import BaseModel
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email is required'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# TODO: Allow users to be able to register and manage their properties not as companies but rather as individuals
class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    companies = models.ManyToManyField(
        Company,
        through='UserCompanyAccess',
        through_fields=('user', 'company'),
        related_name='users',
        verbose_name=_('Companies'),
    )
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(unique=True, default=uuid.uuid4)

    def generate_verification_token(self):
        self.email_verification_token = uuid.uuid4()
        self.save()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    

class UserTypeEnums(models.TextChoices):
    SUPERADMIN = 'sa', _('Superadmin')
    SUBADMIN = 'su', _('Subadmin')
    COMPANY_OWNER = 'co', _('Company Owner')
    COMPANY_USER = 'cu', _('Company User')
    TENANT = 'te', _('Tenant') # Tenant
    BUYER = 'bu', _('Buyer') # Buyer
    
class UserCompanyAccess(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    access_level = models.CharField(max_length=2, choices=UserTypeEnums.choices)

    class Meta:
        # This ensures that a user can only have one access level per company
        # For example, a user cannot be both a Company Owner and Company User for the same company
        unique_together = ('user', 'company', 'access_level')

    def __str__(self):
        return f"{self.user.email} - {self.company.name} - {self.get_access_level_display()}"

    def clean(self):
        if self.access_level in [UserTypeEnums.SUPERADMIN, UserTypeEnums.SUBADMIN]:
            raise ValidationError("Superadmin and Subadmin cannot be assigned to any company.")