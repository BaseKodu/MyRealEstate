from typing import Any, Dict
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .utils import getCurrentCompany
from .mixins import CompanyRequiredMixin
from icecream import ic
from django.contrib.contenttypes.models import ContentType
from myrealestate.properties.models import PropertyImage, Estate, Building, Unit, SubUnit
from myrealestate.common.forms import PropertyImageForm


class TitleMixin:
    """Mixin to add title to context"""
    title: str = ""
    
    def get_title(self) -> str:
        """Get the page title."""
        return self.title
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        return context

class CompanyViewMixin:
    """Mixin to handle company-specific operations"""
    def get_company(self):
        return getCurrentCompany(self.request)

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by company if the model has company field
        if hasattr(self.model, 'company'):
            return queryset.filter(company=self.get_company())
        return queryset

class BaseListView(CompanyRequiredMixin, CompanyViewMixin, TitleMixin, ListView):
    """Base list view with search and pagination"""
    template_name = "commons/list.html"
    paginate_by = 10
    search_fields = []  # Fields to search in
    ordering = "-created_at"  # Default ordering
    
    def get_queryset(self):
        # First get company-filtered queryset
        queryset = super().get_queryset()
        
        # Then apply search if query exists
        search_query = self.request.GET.get("q")
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
            
        # Apply ordering
        if self.ordering:
            queryset = queryset.order_by(self.ordering)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "search_query": self.request.GET.get("q", ""),
            "can_add": self.has_add_permission(),
            "can_edit": self.has_change_permission(),
            "can_delete": self.has_delete_permission(),
            'app_name': self.model._meta.app_label,
            'model_name': self.model._meta.model_name,
        })
        return context
    
    def has_add_permission(self):
        """Check if user can add objects"""
        return True
    
    def has_change_permission(self):
        """Check if user can change objects"""
        return True
    
    def has_delete_permission(self):
        """Check if user can delete objects"""
        return True

class BaseCreateView(CompanyRequiredMixin, CompanyViewMixin, TitleMixin, CreateView):
    """Base create view"""
    template_name = "common/form.html"
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.get_company()
        return kwargs
    
    def form_valid(self, form):
        """Handle form submission"""
        #ic("Form valid called")
        response = super().form_valid(form)
        messages.success(self.request, f"{self.model._meta.verbose_name} created successfully.")
        #ic("Form valid response:", response)
        return response
    
    def post(self, request, *args, **kwargs):
        ic("POST received:", request.POST)  # Debug POST data
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        """Get URL to redirect to after successful creation"""
        if hasattr(self, 'success_url') and self.success_url:
            return self.success_url
        return reverse(f"{self.model._meta.app_label}:{self.model._meta.model_name}_list")


class DeleteViewMixin(CompanyViewMixin):
    """Mixin to handle AJAX delete requests"""
    
    def delete(self, request, *args, **kwargs):
        """Handle delete request"""
        self.object = self.get_object()
        object_name = str(self.object)
        
        try:
            self.object.delete()
            messages.success(request, f"{self.model._meta.verbose_name} '{object_name}' deleted successfully.")
            return JsonResponse({
                "status": "success",
                "message": f"{self.model._meta.verbose_name} deleted successfully.",
                "redirect_url": self.get_success_url()
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
    
    def get(self, request, *args, **kwargs):
        """Return HTML for delete confirmation modal"""
        self.object = self.get_object()
        context = self.get_context_data()
        html = render_to_string("commons/delete_modal.html", context, request)
        return JsonResponse({"html": html})
    

class PatchHandlerMixin:
    """
    Mixin to handle PATCH requests through POST method with a hidden _method field.
    Allows handling partial updates through standard HTML forms.
    """
    def post(self, request, *args, **kwargs):
        if request.POST.get('_method', '').upper() == 'PATCH':
            if hasattr(self, 'patch'):
                return self.patch(request, *args, **kwargs)
            return HttpResponseBadRequest('PATCH method not implemented')
        return super().post(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        """
        Default patch implementation - override in child classes for custom behavior
        Treats PATCH similar to POST but expects partial updates
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
    

class BaseUpdateView(CompanyRequiredMixin, CompanyViewMixin, TitleMixin, PatchHandlerMixin, UpdateView):
    """Base update view with PATCH support"""
    template_name = "common/form.html"
    
    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests for partial updates
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            # Only update fields that were actually submitted
            for field, value in form.cleaned_data.items():
                if field in request.POST:
                    setattr(self.object, field, value)
            self.object.save()
            messages.success(request, f"{self.model._meta.verbose_name} partially updated successfully.")
            return self.form_valid(form)
        return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = False
        return context
    
    def get_success_url(self):
        """Get URL to redirect to after successful update"""
        if hasattr(self, 'success_url') and self.success_url:
            return self.success_url
        return reverse(f"{self.model._meta.app_label}:{self.model._meta.model_name}_list")
    
    def form_valid(self, form):
        """Add success message on valid form submission"""
        response = super().form_valid(form)
        messages.success(self.request, f"{self.model._meta.verbose_name} updated successfully.")
        return response
    


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