from django.db import models
from django.db.models import Q, Count, Exists, OuterRef
from django.utils import timezone
from django.core.exceptions import ValidationError
from myrealestate.common.models import BaseModel
from myrealestate.accounts.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from datetime import datetime

from myrealestate.common.storage import CustomS3Boto3Storage
import logging

logger = logging.getLogger(__name__)

class BuildingTypeEnums(models.TextChoices):
   MULTI_UNIT = 'M', 'Multi Unit'
   SINGLE_UNIT = 'S', 'Single Unit'
   COMPLEX = 'C', 'Complex'

class UnitTypeEnums(models.TextChoices):
   APARTMENT = 'A', 'Apartment'
   HOUSE = 'H', 'House'
   OFFICE = 'O', 'Office'

class EstateTypeEnums(models.TextChoices):
   RESIDENTIAL = 'R', 'Residential'
   COMMERCIAL = 'C', 'Commercial'
   MIXED = 'M', 'Mixed Use'

class SubUnitTypeEnums(models.TextChoices):
   ROOM = 'R', 'Room'
   STORE = 'S', 'Store'
   OFFICE = 'O', 'Office'

class BuildingManager(models.Manager):
   def get_queryset(self):
       return super().get_queryset()
   
   def with_vacancy_status(self):
       return self.annotate(
           total_units=Count('units'),
           vacant_units=Count('units', filter=Q(units__is_vacant=True))
       )
   
   def standalone_houses(self):
       return self.filter(building_type=BuildingTypeEnums.SINGLE_UNIT)
   
   def apartment_buildings(self):
       return self.filter(building_type=BuildingTypeEnums.MULTI_UNIT)
   
   def with_available_units(self):
       return self.filter(units__is_vacant=True).distinct()

class Estate(BaseModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="owned_estates")
    total_buildings = models.IntegerField(default=0)
    amenities = models.JSONField(null=True, blank=True)
    estate_type = models.CharField(max_length=1, choices=EstateTypeEnums.choices, default=EstateTypeEnums.RESIDENTIAL)
    managing = models.BooleanField(default=False, help_text="Select if you or your company is managing this estate")
    images = GenericRelation('PropertyImage', related_query_name='estate')

    def __str__(self):
        return self.name

class Building(BaseModel):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name="buildings", null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="owned_buildings")
    name = models.CharField(max_length=255)
    building_type = models.CharField(max_length=1, choices=BuildingTypeEnums.choices, default=BuildingTypeEnums.MULTI_UNIT)
    address = models.CharField(max_length=500, null=True, blank=True)
    managing = models.BooleanField(default=False, help_text="Select if you or your company is managing this building")
    images = GenericRelation('PropertyImage', related_query_name='building')

    objects = BuildingManager()

    class Meta:
       indexes = [
           models.Index(fields=['building_type']),
           models.Index(fields=['estate', 'building_type']),
           models.Index(fields=['name']),
       ]

    def clean(self):
        pass # validation should be handled once we have a pk for the building
        # Remove any validation that assumes building company must match estate company
        #if self.building_type == BuildingTypeEnums.SINGLE_UNIT:
        #    if self.units.count() > 1:
        #        raise ValidationError("Single unit buildings can only have one unit")

    def save(self, *args, **kwargs):
        '''
        Ensure that when object is created and unit type is multi unit, a unit is created
        '''
        instance_exists = Building.objects.filter(pk=self.pk).exists()
        super().save(*args, **kwargs)
        if not instance_exists and self.building_type == BuildingTypeEnums.SINGLE_UNIT:
            Unit.objects.create(building=self, company=self.company, number=1, unit_type=UnitTypeEnums.HOUSE)


    @property
    def is_standalone(self):
        return self.building_type == BuildingTypeEnums.SINGLE_UNIT

    @property
    def can_have_multiple_units(self):
        return self.building_type == BuildingTypeEnums.MULTI_UNIT

    def __str__(self):
        if self.estate:
            return f"{self.name} in {self.estate.name}"
        return self.name

class UnitManager(models.Manager):
   def get_queryset(self):
       return super().get_queryset()
   
   def available(self):
       return self.filter(
           is_vacant=True,
           available_from__lte=timezone.now().date()
       )
   
   def with_subletting_info(self):
       return self.annotate(
           total_subunits=Count('subunits'),
           vacant_subunits=Count('subunits', filter=Q(subunits__is_vacant=True))
       )
   
   def standalone_houses(self):
       return self.filter(
           building__building_type=BuildingTypeEnums.SINGLE_UNIT,
           unit_type=UnitTypeEnums.HOUSE
       )
   
   def apartments(self):
       return self.filter(
           building__building_type=BuildingTypeEnums.MULTI_UNIT,
           unit_type=UnitTypeEnums.APARTMENT
       )
   
   def in_price_range(self, min_price, max_price):
       query = self.all()
       if min_price is not None:
           query = query.filter(base_rent__gte=min_price)
       if max_price is not None:
           query = query.filter(base_rent__lte=max_price)
       return query

class Unit(BaseModel):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="units")
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="owned_units")

    number = models.CharField(max_length=50)
    unit_type = models.CharField(max_length=1, choices=UnitTypeEnums.choices)
    main_tenant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="units")
    is_vacant = models.BooleanField(default=True)
    square_footage = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=1)
    furnished = models.BooleanField(default=False)
    available_from = models.DateField(null=True, blank=True)
    base_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    features = models.JSONField(null=True, blank=True)
    images = GenericRelation('PropertyImage', related_query_name='unit')

    objects = UnitManager()

    class Meta:
       indexes = [
           models.Index(fields=['is_vacant']),
           models.Index(fields=['base_rent']),
           models.Index(fields=['unit_type', 'is_vacant']),
           models.Index(fields=['building', 'is_vacant']),
           models.Index(fields=['available_from']),
           models.Index(fields=['bedrooms']),
       ]
       unique_together = ['building', 'number']

    def clean(self):
       if self.building.building_type == BuildingTypeEnums.SINGLE_UNIT:
           if self.building.units.exclude(pk=self.pk).exists():
               raise ValidationError("Single unit buildings can only have one unit")
           # self.number = self.building.name
           
       if self.building.building_type == BuildingTypeEnums.MULTI_UNIT:
           if self.unit_type != UnitTypeEnums.APARTMENT:
               raise ValidationError("Multi-unit buildings can only have apartment units")
       elif self.building.building_type == BuildingTypeEnums.SINGLE_UNIT:
           if self.unit_type != UnitTypeEnums.HOUSE:
               raise ValidationError("Single unit buildings can only be houses")

    @property
    def is_standalone_house(self):
        return (self.building.building_type == BuildingTypeEnums.SINGLE_UNIT and 
                self.unit_type == UnitTypeEnums.HOUSE)

    @property
    def full_address(self):
        if self.is_standalone_house:
            return self.building.address
        return f"Unit {self.number}, {self.building.name}"

    def __str__(self):
        return f"Unit {self.number} in {self.building.name}"

class SubUnitManager(models.Manager):
   def get_queryset(self):
       return super().get_queryset()
   
   def available(self):
       return self.filter(
           is_vacant=True,
           available_from__lte=timezone.now().date()
       )
   
   def in_price_range(self, min_price, max_price):
       query = self.all()
       if min_price is not None:
           query = query.filter(base_rent__gte=min_price)
       if max_price is not None:
           query = query.filter(base_rent__lte=max_price)
       return query

class SubUnit(BaseModel):
   parent_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="subunits")
   number = models.CharField(max_length=50)
   subunit_type = models.CharField(max_length=1, choices=SubUnitTypeEnums.choices, default=SubUnitTypeEnums.ROOM)
   sublet_tenant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="subunits")
   furnished = models.BooleanField(default=False)
   available_from = models.DateField(null=True, blank=True)
   base_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True)
   deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
   is_vacant = models.BooleanField(default=True)
   images = GenericRelation('PropertyImage', related_query_name='subunit')

   objects = SubUnitManager()

   class Meta:
       indexes = [
           models.Index(fields=['is_vacant']),
           models.Index(fields=['base_rent']),
           models.Index(fields=['available_from']),
           models.Index(fields=['parent_unit', 'is_vacant']),
       ]

   def __str__(self):
       return f"SubUnit {self.number} in {self.parent_unit}"
   



# TODO: Address model. Keep addresses simple for now. We are gonna intergrate with google maps api
#class Address(BaseModel):


def validate_file_size(value):
    """Validate that file size is under 5MB"""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError(_("Maximum file size is 5MB"))
    

def property_image_path(instance, filename):
    """Generate path: property_images/company_id/property_type/property_id/filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = filename.split('.')[-1]
    filename = f"{timestamp}.{ext}"
    
    company_id = instance.property_object.company.id
    property_type = instance.content_type.model.lower()
    
    return f'property_images/{company_id}/{property_type}s/{instance.object_id}/{filename}'

class PropertyImage(BaseModel):
    """Generic image model that can be associated with Estate, Building, Unit, or SubUnit"""
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ('estate', 'building', 'unit', 'subunit')
        }
    )
    object_id = models.PositiveIntegerField()
    property_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to=property_image_path, validators=[validate_file_size], storage=CustomS3Boto3Storage())
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_primary']),
            models.Index(fields=['order']),
        ]
        ordering = ['order', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'is_primary'],
                condition=models.Q(is_primary=True),
                name='unique_primary_image_per_object'
            )
        ]

    def clean(self):
        """Ensure image limits are respected"""
        if not self.pk:  # Only check on creation
            existing_count = PropertyImage.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id
            ).count()
            if existing_count >= 50:
                raise ValidationError(_("Maximum number of images (50) reached for this property."))

    def save(self, *args, **kwargs):
        """Handle primary image logic"""
        if self.is_primary:
            # Set all other images of this object to not primary
            PropertyImage.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
            
        # If this is the first image, make it primary
        elif not self.pk and not PropertyImage.objects.filter(
            content_type=self.content_type,
            object_id=self.object_id
        ).exists():
            self.is_primary = True
            
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Ensure there's always a primary image if images exist"""
        was_primary = self.is_primary
        super().delete(*args, **kwargs)
        
        if was_primary:
            # Try to set another image as primary
            remaining_image = PropertyImage.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id
            ).first()
            if remaining_image:
                remaining_image.is_primary = True
                remaining_image.save()

    def __str__(self):
        return f"Image for {self.content_type.model} ({self.object_id})"