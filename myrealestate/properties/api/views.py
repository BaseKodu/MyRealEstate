from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from myrealestate.properties.models import Estate, Building, Unit, SubUnit, PropertyImage
from .serializers import (
    EstateSerializer, BuildingSerializer, UnitSerializer,
    SubUnitSerializer, PropertyImageSerializer, PropertyImageUploadSerializer
)
import logging

logger = logging.getLogger(__name__)

class BasePropertyViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

class EstateViewSet(BasePropertyViewSet):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(managing=True)
        return queryset

class BuildingViewSet(BasePropertyViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer

class UnitViewSet(BasePropertyViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

class SubUnitViewSet(viewsets.ModelViewSet):
    queryset = SubUnit.objects.all()
    serializer_class = SubUnitSerializer
    
    def get_queryset(self):
        return self.queryset.filter(parent_unit__company=self.request.user.company)

class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        return self.queryset.filter(
            property_object__company=self.request.user.company
        )
    
    @action(detail=False, methods=['post'], url_path='upload/(?P<property_type>[^/.]+)/(?P<property_id>[^/.]+)')
    def upload_image(self, request, property_type, property_id):
        serializer = PropertyImageUploadSerializer(
            data=request.data,
            context={
                'request': request,
                'property_type': property_type,
                'property_id': property_id
            }
        )
        
        if serializer.is_valid():
            image = serializer.save()
            return Response(
                PropertyImageSerializer(image).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        image = self.get_object()
        image.is_primary = True
        image.save()
        return Response({'status': 'primary image set'}) 