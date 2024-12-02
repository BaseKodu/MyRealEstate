# context_processors.py
from .storage import StorageHealthCheck

def storage_status(request):
    """Make storage health status available to all templates"""
    is_healthy, last_checked = StorageHealthCheck.get_status()
    return {
        'storage_healthy': is_healthy,
        'storage_last_checked': last_checked
    }