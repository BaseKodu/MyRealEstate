from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EstateViewSet, BuildingViewSet, UnitViewSet,
    SubUnitViewSet, PropertyImageViewSet
)

router = DefaultRouter()
router.register('estates', EstateViewSet)
router.register('buildings', BuildingViewSet)
router.register('units', UnitViewSet)
router.register('subunits', SubUnitViewSet)
router.register('images', PropertyImageViewSet)

app_name = 'properties-api'

urlpatterns = [
    path('', include(router.urls)),
] 