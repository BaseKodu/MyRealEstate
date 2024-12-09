# commons/views.py
from typing import Any, Dict
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

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

class BaseListView(LoginRequiredMixin, TitleMixin, ListView):
    """Base list view with search and pagination"""
    template_name = "commons/list.html"
    paginate_by = 10
    search_fields = []  # Fields to search in
    ordering = "-created_at"  # Default ordering
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply search if query exists
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

class BaseCreateView(LoginRequiredMixin, TitleMixin, CreateView):
    """Base create view"""
    template_name = "commons/form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context
    
    def get_success_url(self):
        """Get URL to redirect to after successful creation"""
        if hasattr(self, 'success_url') and self.success_url:
            return self.success_url
        return reverse(f"{self.model._meta.app_label}:{self.model._meta.model_name}_list")
    
    def form_valid(self, form):
        """Add success message on valid form submission"""
        response = super().form_valid(form)
        messages.success(self.request, f"{self.model._meta.verbose_name} created successfully.")
        return response

class BaseUpdateView(LoginRequiredMixin, TitleMixin, UpdateView):
    """Base update view"""
    template_name = "commons/form.html"
    
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

class DeleteViewMixin:
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