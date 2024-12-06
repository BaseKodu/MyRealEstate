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
