from rest_framework import serializers
from myrealestate.properties.models import Estate, Building, Unit, SubUnit, PropertyImage
from django.contrib.contenttypes.models import ContentType

class PropertyImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'url', 'caption', 'is_primary', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_url(self, obj):
        return obj.image.url if obj.image else None

class EstateSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Estate
        fields = [
            'id', 'name', 'address', 'company', 'total_buildings',
            'estate_type', 'managing', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

class BuildingSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Building
        fields = [
            'id', 'estate', 'company', 'name', 'building_type',
            'address', 'managing', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

class UnitSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'id', 'building', 'company', 'number', 'unit_type',
            'main_tenant', 'is_vacant', 'square_footage', 'bedrooms',
            'bathrooms', 'furnished', 'available_from', 'base_rent',
            'deposit_amount', 'parking_spots', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

class SubUnitSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = SubUnit
        fields = [
            'id', 'parent_unit', 'number', 'subunit_type',
            'sublet_tenant', 'furnished', 'available_from',
            'base_rent', 'deposit_amount', 'is_vacant',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PropertyImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary', 'order']
    
    def create(self, validated_data):
        request = self.context.get('request')
        property_type = self.context.get('property_type')
        property_id = self.context.get('property_id')
        
        # Get the content type for the property model
        content_type = ContentType.objects.get(
            app_label='properties',
            model=property_type.lower()
        )
        
        # Create the image instance
        image = PropertyImage.objects.create(
            content_type=content_type,
            object_id=property_id,
            **validated_data
        )
        
        return image 