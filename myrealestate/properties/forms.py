from django import forms
from myrealestate.common.forms import BaseModelForm
from myrealestate.properties.models import Estate, Building

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
