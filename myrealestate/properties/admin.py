from django.contrib import admin

# Register your models here.

from .models import Estate, Building, Unit, SubUnit, PropertyImage

admin.site.register(Estate)
admin.site.register(Building)
admin.site.register(Unit)
admin.site.register(SubUnit)
admin.site.register(PropertyImage)
