from django.shortcuts import render, redirect
from myrealestate.common.views import BaseListView, BaseCreateView, DeleteViewMixin
from myrealestate.properties.models import Estate
from myrealestate.properties.forms import EstateForm
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views import View

# Create your views here.


class EstateCreateView(BaseCreateView):
    form_class = EstateForm
    success_url = reverse_lazy("home")
    title = "Create New Estate"

    def form_valid(self, form):
        # TODO: Ensure that save logic for objects with company attribute is handled in a base view or base form in order to keep up with DRY principle
        """Handle form submission"""
        self.object = form.save(commit=False)
        self.object.company = self.get_company()
        self.object.save()
        messages.success(self.request, f"Estate created successfully.")
        return super(BaseCreateView, self).form_valid(form)


class EstateListView(BaseListView):
    model = Estate
    template_name = "properties/estate_list.html"
    context_object_name = "estates"
    title = "Estate List"




class EstateDeleteView(DeleteViewMixin, View):
    model = Estate
    def get_success_url(self):
        return reverse('properties:estate-list')