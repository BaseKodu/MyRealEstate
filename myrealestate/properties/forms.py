from django import forms
from myrealestate.common.forms import BaseModelForm, BasePatchForm
from myrealestate.properties.models import Estate, Building, Unit, Amenity, PropertyFeature

class EstateForm(BaseModelForm):
    class Meta:
        model = Estate
        fields = ['name', 'estate_type', 'managing', 'address']
        labels = {
            'managing': 'Are you managing this estate?'
            #'amenities': 'Estate Amenities'
        }
        #widgets = {
        #    'amenities': forms.CheckboxSelectMultiple()
        #}

class EstatePatchForm(BasePatchForm):
    class Meta:
        model = Estate
        fields = ['name', 'estate_type', 'managing', 'address']
        labels = {
            'managing': 'Are you managing this estate?'
            #'amenities': 'Estate Amenities'
        }
        #widgets = {
        #    'amenities': forms.CheckboxSelectMultiple()
        #}
        



class BuildingForm(BaseModelForm):
    class Meta:
        model = Building
        fields = ['estate', 'name', 'building_type', 'managing', 'address', ]
        labels = {'managing': 'Are you managing this building?'}

class BuildingPatchForm(BasePatchForm, BuildingForm):
    class Meta:
        model = Building
        fields = ['estate', 'name', 'building_type', 'managing', 'address', ]
        labels = {'managing': 'Are you managing this building?'} 


        


class UnitForm(BaseModelForm):
    class Meta:
        model = Unit
        fields = [
            'building', 'number', 'unit_type', 
            'bedrooms', 'bathrooms', 'square_footage', 
            'furnished', 'parking_spots', 'base_rent',
            'deposit_amount', 'available_from',
            'amenities', 'features'
        ]
        labels = {
            'furnished': 'Is the unit furnished?',
            'amenities': 'Unit Amenities',
            'features': 'Unit Features'
        }
        widgets = {
            'amenities': forms.CheckboxSelectMultiple(),
            'features': forms.CheckboxSelectMultiple(),
            'available_from': forms.DateInput(attrs={'type': 'date'})
        }


class UnitPatchForm(BasePatchForm, UnitForm):
    class Meta:
        model = Unit
        fields = [
            'building', 'number', 'unit_type', 
            'bedrooms', 'bathrooms', 'square_footage', 
            'furnished', 'parking_spots', 'base_rent',
            'deposit_amount', 'available_from',
            'amenities', 'features'
        ]
        labels = {
            'furnished': 'Is the unit furnished?',
            'amenities': 'Unit Amenities',
            'features': 'Unit Features'
        }
        widgets = {
            'amenities': forms.CheckboxSelectMultiple(),
            'features': forms.CheckboxSelectMultiple(),
            'available_from': forms.DateInput(attrs={'type': 'date'})
        }
