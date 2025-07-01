from myrealestate.common.views import BaseListView, BaseCreateView, DeleteViewMixin, BaseUpdateView, PropertyImageHandlerMixin, CompanyViewMixin
from myrealestate.properties.models import Estate, Building, Unit, Amenity, PropertyFeature
from myrealestate.properties.forms import EstateForm, BuildingForm, UnitForm, EstatePatchForm, BuildingPatchForm, UnitPatchForm
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views import View
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from .models import PropertyImage, Estate, Building, Unit, SubUnit
from myrealestate.common.forms import PropertyImageForm
import logging
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

logger = logging.getLogger(__name__)


class EstateCreateView(PropertyImageHandlerMixin, BaseCreateView):
    form_class = EstateForm
    success_url = reverse_lazy("home")
    title = "Create New Estate"
    supports_images = False
    is_create = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amenities'] = Amenity.objects.all().order_by('category', 'name')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.get_company()
        self.object.save()
        
        # Save many-to-many relationships
        form.save_m2m()
        
        messages.success(self.request, "Estate created successfully.")
        return super(BaseCreateView, self).form_valid(form)


class EstateListView(BaseListView):
    model = Estate
    template_name = "properties/estate_list.html"
    context_object_name = "estates"
    title = "Estate List"

    def get_queryset(self):
        # Get the company-filtered queryset from parent class
        queryset = super().get_queryset()
        # Add managing=True filter
        return queryset.filter(managing=True)


class EstateDeleteView(DeleteViewMixin, View):
    model = Estate
    def get_success_url(self):
        return reverse('properties:estate-list')
    

class EstateUpdateView(PropertyImageHandlerMixin, BaseUpdateView):
    model = Estate
    form_class = EstatePatchForm
    success_url = reverse_lazy("home")
    title = "Update Estate"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amenities'] = Amenity.objects.all().order_by('category', 'name')
        return context

    def form_valid(self, form):
        #messages.success(self.request, f"Estate updated successfully.")
        return super(BaseUpdateView, self).form_valid(form)
    

class BuildingCreateView(PropertyImageHandlerMixin, BaseCreateView):
    form_class = BuildingForm
    success_url = reverse_lazy("home")
    title = "Create New Building"
    supports_images = False


    def form_valid(self, form):
        # TODO: Ensure that save logic for objects with company attribute is handled in a base view or base form in order to keep up with DRY principle
        """Handle form submission"""
        self.object = form.save(commit=False)
        self.object.company = self.get_company()
        self.object.save()
        messages.success(self.request, f"Building created successfully.")
        return super(BaseCreateView, self).form_valid(form)
    

class BuildingListView(BaseListView):
    model = Building
    template_name = "properties/building_list.html"
    context_object_name = "buildings"
    title = "Building List"


class BuildingUpdateView(PropertyImageHandlerMixin,BaseUpdateView):
    model = Building
    form_class = BuildingPatchForm
    success_url = reverse_lazy("home")
    title = "Update Building"
    supports_images = True

    def form_valid(self, form):
        #messages.success(self.request, f"Building updated successfully.")
        return super(BaseUpdateView, self).form_valid(form)


class UnitCreateView(PropertyImageHandlerMixin, BaseCreateView):
    form_class = UnitForm
    success_url = reverse_lazy("home")
    title = "Create New Unit"
    supports_images = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amenities'] = Amenity.objects.all().order_by('category', 'name')
        context['features'] = PropertyFeature.objects.all().order_by('category', 'name')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.get_company()
        self.object.save()
        
        # Save many-to-many relationships
        form.save_m2m()
        
        messages.success(self.request, "Unit created successfully.")
        return super(BaseCreateView, self).form_valid(form)


class UnitListView(BaseListView):
    model = Unit
    template_name = "properties/unit_list.html"
    context_object_name = "units"
    title = "Unit List"


class UnitUpdateView(PropertyImageHandlerMixin, BaseUpdateView):
    model = Unit
    form_class = UnitPatchForm
    success_url = reverse_lazy("home")
    title = "Update Unit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amenities'] = Amenity.objects.all().order_by('category', 'name')
        context['features'] = PropertyFeature.objects.all().order_by('category', 'name')
        return context

    def form_valid(self, form):
       #messages.success(self.request, f"Unit updated successfully.")
        return super(BaseUpdateView, self).form_valid(form)
    

class PropertyImageUploadView(BaseCreateView):
    model = PropertyImage
    form_class = PropertyImageForm
    http_method_names = ['post']
    title = "Upload Images"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        property_object = self.get_property_object()
        logger.debug(f"Property type: {self.kwargs.get('property_type')}")
        logger.debug(f"Property ID: {self.kwargs.get('property_id')}")
        logger.debug(f"Property object: {property_object}")
        logger.debug(f"Property object type: {type(property_object)}")
        kwargs['property_object'] = property_object
        kwargs['company'] = self.get_company()
        return kwargs

    def get_property_object(self):
        property_type = self.kwargs.get('property_type')
        property_id = self.kwargs.get('property_id')
        
        logger.debug(f"Getting property object for type: {property_type}, id: {property_id}")
        
        model_map = {
            'estate': Estate,
            'building': Building,
            'unit': Unit,
            'subunit': SubUnit
        }
        
        Model = model_map.get(property_type.lower())
        if not Model:
            logger.error(f"Invalid property type: {property_type}")
            raise Http404(f"Invalid property type: {property_type}")
            
        obj = get_object_or_404(
            Model.objects.filter(company=self.get_company()), 
            pk=property_id
        )
        logger.debug(f"Found object: {obj} of type {type(obj)}")
        return obj

    def form_valid(self, form):
        try:
            self.object = form.save()
            return JsonResponse({
                'status': 'success',
                'image_id': self.object.id,
                'url': self.object.image.url,
                'caption': self.object.caption
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


class PropertyImageDeleteView(CompanyViewMixin, View):
    model = PropertyImage
    http_method_names = ['delete']
    
    def get_queryset(self):
        """Ensure users can only delete images from their company's properties"""
        # Get all content types for our property models
        estate_ct = ContentType.objects.get_for_model(Estate)
        building_ct = ContentType.objects.get_for_model(Building)
        unit_ct = ContentType.objects.get_for_model(Unit)
        subunit_ct = ContentType.objects.get_for_model(SubUnit)
        
        company = self.get_company()
        
        # Filter images based on content type and company ownership
        return PropertyImage.objects.filter(
            (
                (Q(content_type=estate_ct) & Q(object_id__in=Estate.objects.filter(company=company).values('id'))) |
                (Q(content_type=building_ct) & Q(object_id__in=Building.objects.filter(company=company).values('id'))) |
                (Q(content_type=unit_ct) & Q(object_id__in=Unit.objects.filter(company=company).values('id'))) |
                (Q(content_type=subunit_ct) & Q(object_id__in=SubUnit.objects.filter(parent_unit__company=company).values('id')))
            )
        )

    def get_object(self, queryset=None):
        """Get the image object to delete"""
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        """Handle delete request"""
        try:
            instance = self.get_object()
            instance.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Image deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


class PropertyImageSetPrimaryView(BaseUpdateView):
    model = PropertyImage
    http_method_names = ['post']
    
    def get_queryset(self):
        """Ensure users can only modify images from their company's properties"""
        return PropertyImage.objects.filter(
            content_type__model__in=['estate', 'building', 'unit', 'subunit'],
            property_object__company=self.get_company()
        )

    def post(self, request, *args, **kwargs):
        """Handle setting an image as primary"""
        try:
            image = self.get_object()
            
            # Set this image as primary (model's save method will handle updating others)
            image.is_primary = True
            image.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Image set as primary successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

# URLS

from django.urls import path
from myrealestate.properties.views import EstateCreateView, EstateListView, EstateDeleteView, BuildingCreateView, BuildingListView, BuildingUpdateView, UnitCreateView, UnitListView, UnitUpdateView, EstateUpdateView, PropertyImageUploadView, PropertyImageDeleteView, PropertyImageSetPrimaryView


app_name = "properties"

urlpatterns = [
    # Estates
    path("estates/new/", EstateCreateView.as_view(), name="create-estate"),
    path("estates/", EstateListView.as_view(), name="estate-list"),
    path('estates/<int:pk>/delete/', EstateDeleteView.as_view(), name='delete-estate'),
    path('estates/<int:pk>/update/', EstateUpdateView.as_view(), name='update-estate'),

    # Buildings
    path("buildings/new/", BuildingCreateView.as_view(), name="create-building"),
    path("buildings/", BuildingListView.as_view(), name="building-list"),
    path('buildings/<int:pk>/update/', BuildingUpdateView.as_view(), name='update-building'),
    #path('buildings/<int:pk>/delete/', BuildingDeleteView.as_view(), name='delete-building'),

    # Units
    path("units/new/", UnitCreateView.as_view(), name="create-unit"),
    path("units/", UnitListView.as_view(), name="unit-list"),
    path('units/<int:pk>/update/', UnitUpdateView.as_view(), name='update-unit'),


    # Image handling URLs
    path(
        '<str:property_type>/<int:property_id>/upload-images/',
        PropertyImageUploadView.as_view(),
        name='property-image-upload'
    ),
    path(
        'images/<int:pk>/delete/',
        PropertyImageDeleteView.as_view(),
        name='property-image-delete'
    ),
    path(
        'images/<int:pk>/set-primary/',
        PropertyImageSetPrimaryView.as_view(),
        name='property-image-set-primary'
    ),
]
