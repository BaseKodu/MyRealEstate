from django.urls import path
from myrealestate.properties.views import EstateCreateView


app_name = "properties"

urlpatterns = [
    path("new/", EstateCreateView.as_view(), name="create-estate"),
]
