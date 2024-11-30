from django import forms
from myrealestate.common.forms import BaseModelForm
from myrealestate.properties.models import Estate, Building, Unit

class EstateForm(BaseModelForm):
    class Meta:
        model = Estate
        fields = ['name', 'estate_type', 'managing', 'address', ]
        labels = {'managing': 'Are you managing this estate?'}


class BuildingForm(BaseModelForm):
    class Meta:
        model = Building
        fields = ['estate', 'name', 'building_type', 'managing', 'address', ]
        labels = {'managing': 'Are you managing this building?'}


class UnitForm(BaseModelForm):
    class Meta:
        model = Unit
        fields = ['building', 'number', 'unit_type', 'bedrooms', 'bathrooms', 'square_footage', 'furnished']
        labels = {'furnished': 'Is the unit furnished?'}
