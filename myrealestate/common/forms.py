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
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        # Ensure _method is always first in field order
        field_order = ['_method'] + [f for f in self.fields if f != '_method']
        self.order_fields(field_order)
        
        # Make all fields optional for PATCH requests
        if self.data.get('_method') == 'PATCH':
            for field_name, field in self.fields.items():
                if field_name != '_method':
                    field.required = False
        
        self.style_fields()

    def clean(self):
        """
        For PATCH requests, only validate fields that were actually submitted.
        This allows partial updates without requiring all fields.
        """
        cleaned_data = super().clean()
        
        if self.data.get('_method') == 'PATCH' and self.instance.pk:
            # For fields not in the submitted data, use the existing values
            for field_name, field in self.fields.items():
                if field_name not in self.data and field_name != '_method':
                    # Skip validation for this field
                    if field_name in self.errors:
                        del self.errors[field_name]
                    
                    # Use existing value from the instance
                    if hasattr(self.instance, field_name):
                        cleaned_data[field_name] = getattr(self.instance, field_name)
        
        return cleaned_data

    def save(self, commit=True):
        """
        For PATCH requests, only update fields that were actually submitted.
        """
        if self.data.get('_method') == 'PATCH' and self.instance.pk:
            # Get the current instance from the database
            instance = self.instance.__class__.objects.get(pk=self.instance.pk)
            
            # Get list of many-to-many fields
            m2m_fields = [f.name for f in self._meta.model._meta.many_to_many]
            
            # Only update fields that were in the submitted data
            for field_name in self.fields:
                if field_name in self.data and field_name != '_method':
                    # Skip many-to-many fields, they'll be handled separately
                    if field_name not in m2m_fields:
                        setattr(self.instance, field_name, self.cleaned_data.get(field_name))
            
            # Handle many-to-many fields separately
            if commit:
                self.instance.save()
                
                # Handle M2M fields that were in the submitted data
                for field_name in m2m_fields:
                    if field_name in self.data and field_name != '_method':
                        # Get the related manager
                        related_manager = getattr(self.instance, field_name)
                        # Get the new values from cleaned_data
                        new_values = self.cleaned_data.get(field_name)
                        if new_values is not None:
                            # Clear and set the new values
                            related_manager.clear()
                            related_manager.add(*new_values)
                
            return self.instance
        else:
            # For non-PATCH requests, use the standard save method
            return super().save(commit)


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