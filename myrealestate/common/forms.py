from django import forms
from icecream import ic
from django.contrib.contenttypes.models import ContentType
from myrealestate.properties.models import PropertyImage

class DaisyFormMixin:
    """Mixin to add DaisyUI styling to form fields"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()

    def style_fields(self):
        """Apply DaisyUI classes to form fields"""
        for field_name, field in self.fields.items():
            # Base classes for all inputs
            base_classes = ['input input-bordered w-full']
            
            # Apply specific classes based on field type
            if isinstance(field.widget, forms.CheckboxInput):
                base_classes = ['checkbox checkbox-primary']
            elif isinstance(field.widget, forms.Select):
                base_classes = ['select select-bordered w-full']
            elif isinstance(field.widget, forms.Textarea):
                base_classes = ['textarea textarea-bordered w-full']
            elif isinstance(field.widget, forms.RadioSelect):
                base_classes = ['radio radio-primary']
            elif isinstance(field.widget, forms.FileInput):
                base_classes = ['file-input file-input-bordered w-full']
            elif isinstance(field.widget, forms.DateInput):
                base_classes = ['input input-bordered w-full']
                field.widget.attrs['type'] = 'date'
            elif isinstance(field.widget, forms.TimeInput):
                base_classes = ['input input-bordered w-full']
                field.widget.attrs['type'] = 'time'
            elif isinstance(field.widget, forms.DateTimeInput):
                base_classes = ['input input-bordered w-full']
                field.widget.attrs['type'] = 'datetime-local'
            
            # Add size classes if specified
            if hasattr(field, 'size'):
                if field.size == 'sm':
                    base_classes.append('input-sm')
                elif field.size == 'lg':
                    base_classes.append('input-lg')
            
            # Add error class if field has errors
            if hasattr(field, 'errors') and field.errors:
                base_classes.append('input-error')
            
            # Add disabled class if field is disabled
            if field.widget.attrs.get('disabled'):
                base_classes.append('input-disabled')
            
            # Join classes and set on widget
            field.widget.attrs['class'] = ' '.join(base_classes)
            
            # Add placeholder if not present
            if not field.widget.attrs.get('placeholder') and not isinstance(
                field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.FileInput)
            ):
                field.widget.attrs['placeholder'] = field.label or field_name.title()

# Rest of your classes remain the same...


class BaseForm(DaisyFormMixin, forms.Form):
    """Base form with DaisyUI styling"""
    pass

class BaseModelForm(DaisyFormMixin, forms.ModelForm):
    """Base model form with DaisyUI styling"""
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        self.style_fields()

    def save(self, commit=True):
        """Standard save without company logic"""
        return super().save(commit)

class ButtonStyles:
    """Helper class for DaisyUI button styling"""
    @staticmethod
    def get_classes(variant='primary', size=None, outline=False, additional_classes=None):
        """
        Get DaisyUI button classes
        variant: primary, secondary, accent, info, success, warning, error
        size: lg, sm, xs
        outline: True/False
        """
        classes = ['btn']
        
        # Add variant
        if variant:
            if outline:
                classes.append(f'btn-outline btn-{variant}')
            else:
                classes.append(f'btn-{variant}')
        
        # Add size
        if size:
            classes.append(f'btn-{size}')
            
        # Add additional classes
        if additional_classes:
            classes.extend(additional_classes)
            
        return ' '.join(classes)


class BasePatchForm(BaseModelForm):
    """Base form for PATCH requests with DaisyUI styling"""
    _method = forms.CharField(
        widget=forms.HiddenInput(),
        initial='PATCH',
        required=False
    )

    class Meta:
        model = None
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure _method is always first in field order
        field_order = ['_method'] + [f for f in self.fields if f != '_method']
        self.order_fields(field_order)


class PropertyImageForm(BaseModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption']

    def __init__(self, *args, property_object=None, **kwargs):
        self.property_object = property_object
        super().__init__(*args, **kwargs)
        
        # Customize file input
        self.fields['image'].widget.attrs.update({
            'class': 'hidden',  # Hidden because we'll use custom UI
            'data-max-files': '50',
            'data-max-size': '5',  # in MB
            'accept': 'image/*'
        })
        
        if property_object:
            self.fields['image'].widget.attrs.update({
                'data-property-type': property_object._meta.model_name,
                'data-property-id': property_object.id
            })

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.property_object:
            instance.content_type = ContentType.objects.get_for_model(self.property_object)
            instance.object_id = self.property_object.id
        if commit:
            instance.save()
        return instance