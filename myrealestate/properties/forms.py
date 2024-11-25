from django import forms
from myrealestate.common.forms import BaseModelForm
from myrealestate.properties.models import Estate

class EstateForm(BaseModelForm):
    class Meta:
        model = Estate
        fields = ['name', 'estate_type']