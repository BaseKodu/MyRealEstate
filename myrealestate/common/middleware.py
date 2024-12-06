from django.contrib import messages
from .storage import StorageHealthCheck

class StorageHealthMiddleware:
    """
    Middleware that checks storage health and adds a warning message
    without blocking any functionality
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check storage health only when needed (file operations or viewing images)
        if self._should_check_storage(request):
            is_healthy, last_checked = StorageHealthCheck.get_status()
            if not is_healthy:
                messages.warning(
                    request,
                    "Storage system is currently unavailable. Image uploads and viewing will be temporarily disabled. "
                    "You can continue using other features of the application."
                )

        response = self.get_response(request)
        return response

    def _should_check_storage(self, request):
        """
        Determine if we should check storage health based on the request
        """
        # Check on file uploads
        if request.method in ['POST', 'PUT', 'PATCH'] and request.FILES:
            return True
            
        # Check on image-related URLs (customize these patterns for your app)
        image_related_paths = [
            '/property/images/',
            '/upload/',
            '/documents/',
            # Add other relevant paths
        ]
        
        return any(path in request.path for path in image_related_paths)