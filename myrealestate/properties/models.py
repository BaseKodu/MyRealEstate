from django.db import models
from django.db.models import Q, Count, Exists, OuterRef
from django.utils import timezone
from django.core.exceptions import ValidationError
from myrealestate.common.models import BaseModel
from myrealestate.accounts.models import User

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

    def __str__(self):
        return self.name

class Building(BaseModel):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name="buildings", null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="owned_buildings")
    name = models.CharField(max_length=255)
    building_type = models.CharField(max_length=1, choices=BuildingTypeEnums.choices, default=BuildingTypeEnums.MULTI_UNIT)
    address = models.CharField(max_length=500, null=True, blank=True)
    managing = models.BooleanField(default=False, help_text="Select if you or your company is managing this building")

    objects = BuildingManager()

    class Meta:
       indexes = [
           models.Index(fields=['building_type']),
           models.Index(fields=['estate', 'building_type']),
           models.Index(fields=['name']),
       ]

    def clean(self):
        # Remove any validation that assumes building company must match estate company
        if self.building_type == BuildingTypeEnums.SINGLE_UNIT:
            if self.units.count() > 1:
                raise ValidationError("Single unit buildings can only have one unit")

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