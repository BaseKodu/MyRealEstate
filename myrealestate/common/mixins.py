from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .utils import getCurrentCompany
from django.core.exceptions import ValidationError
from .storage import StorageHealthCheck
from myrealestate.config.settings import MAX_IMAGE_COUNT


class CompanyRequiredMixin(LoginRequiredMixin):
    """
    Mixin that adds current company to the view.
    Must be used with View classes.
    """
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.company = getCurrentCompany(request)
        except PermissionDenied as e:
            messages.error(request, str(e))
            self.handle_no_company()

    def handle_no_company(self):
        """Override this method to customize the no-company behavior"""
        raise PermissionDenied("No company access")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.company
        return context
    


class StorageHealthMixin:
    """Mixin to check storage health for views"""
    storage_error_url = None  # Override this in your view
    storage_error_message = "Storage system is currently unavailable. Please try again later."

    def dispatch(self, request, *args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH'] and request.FILES:
            is_healthy, _ = StorageHealthCheck.get_status()
            if not is_healthy:
                messages.error(request, self.storage_error_message)
                return redirect(self.storage_error_url or 'home')
        return super().dispatch(request, *args, **kwargs)

class ImageStorageMixin(StorageHealthMixin):
    """Specific mixin for property image handling"""
    max_images = MAX_IMAGE_COUNT

    def validate_image_limit(self, property_instance):
        """Check if property has reached image limit"""
        current_count = property_instance.images.count()
        if current_count >= self.max_images:
            raise ValidationError(f"Maximum number of images ({self.max_images}) reached.")