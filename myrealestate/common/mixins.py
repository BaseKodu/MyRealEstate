# mixins.py
from django.shortcuts import render

class PatchHandlerMixin:
    """
    Mixin to handle PATCH requests through POST method with a hidden _method field.
    Returns rendered template instead of JSON.
    """
    def post(self, request, *args, **kwargs):
        if request.POST.get('_method') == 'PATCH':
            if hasattr(self, 'patch'):
                return self.patch(request, *args, **kwargs)
            return HttpResponseBadRequest('PATCH method not implemented')
        return super().post(request, *args, **kwargs)