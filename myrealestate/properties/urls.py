from django.urls import path
from myrealestate.properties.views import EstateCreateView, EstateListView


app_name = "properties"

urlpatterns = [
    path("new/", EstateCreateView.as_view(), name="create-estate"),
    path("", EstateListView.as_view(), name="estate-list"),
]
