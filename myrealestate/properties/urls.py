from django.urls import path
from myrealestate.properties.views import EstateCreateView, EstateListView, EstateDeleteView


app_name = "properties"

urlpatterns = [
    # Estates
    path("estates/new/", EstateCreateView.as_view(), name="create-estate"),
    path("estates/", EstateListView.as_view(), name="estate-list"),
    path('estates/<int:pk>/delete/', EstateDeleteView.as_view(), name='delete-estate'),

]
