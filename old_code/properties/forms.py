from django import forms
from myrealestate.common.forms import BaseModelForm, BasePatchForm
from myrealestate.properties.models import Estate, Building, Unit, Amenity, PropertyFeature
from django.contrib.contenttypes.models import ContentType

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



class PropertyImageForm(BaseModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption']

    def __init__(self, *args, property_object=None, **kwargs):
        self.property_object = property_object
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not self.property_object:
            raise forms.ValidationError("Property object is required")
        
        # Set content_type and object_id on the instance before validation
        self.instance.content_type = ContentType.objects.get_for_model(self.property_object.__class__)
        self.instance.object_id = self.property_object.id
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Content type and object_id are already set in clean()
        
        # Set company from the property object
        if hasattr(self.property_object, 'company'):
            instance.company = self.property_object.company
        
        if commit:
            instance.save()
        return instance
    
class PropertyImageHandlerMixin:
    """Mixin to add image handling capabilities to views"""
    supports_images = True  # Flag to indicate image support
    
    @property
    def model_name(self):
        """Return the model name for use in templates"""
        return self.model.__name__
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'object') and self.object:
            context['images'] = self.object.images.all()
            context['supports_images'] = self.supports_images
        return context

    def handle_image_upload(self, request, property_object):
        form = PropertyImageForm(
            request.POST, 
            request.FILES,
            property_object=property_object,
            company=self.get_company()
        )
        
        if form.is_valid():
            image = form.save()
            return JsonResponse({
                'status': 'success',
                'image_id': image.id,
                'url': image.image.url,
                'caption': image.caption
            })
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        }, status=400)