# Generated by Django 5.1.3 on 2025-02-24 17:37

from django.db import migrations



def add_initial_data(apps, schema_editor):
    Amenity = apps.get_model('properties', 'Amenity')
    PropertyFeature = apps.get_model('properties', 'PropertyFeature')

    # Usage of lucide icons
    INITIAL_AMENITIES = [
        # Security & Access
        {'name': '24/7 Security', 'category': 'security', 'icon': 'Shield'},
        {'name': 'CCTV', 'category': 'security', 'icon': 'Camera'},
        {'name': 'Gated Community', 'category': 'security', 'icon': 'Lock'},
        
        # Recreation
        {'name': 'Swimming Pool', 'category': 'recreation', 'icon': 'Waves'},
        {'name': 'Gym', 'category': 'recreation', 'icon': 'Dumbbell'},
        {'name': 'Tennis Court', 'category': 'recreation', 'icon': 'CircleDot'},
        {'name': 'Basketball Court', 'category': 'recreation', 'icon': 'CircleDot'},
        {'name': 'Playground', 'category': 'recreation', 'icon': 'Trees'},
        
        # Parking
        {'name': 'Covered Parking', 'category': 'parking', 'icon': 'Car'},
        {'name': 'Visitor Parking', 'category': 'parking', 'icon': 'Cars'},
        
        # Building Services
        {'name': 'Elevator', 'category': 'services', 'icon': 'ArrowBigUp'},
        {'name': 'Waste Management', 'category': 'services', 'icon': 'Trash2'},
    ]

    INITIAL_FEATURES = [
        # Climate Control
        {'name': 'Air Conditioning', 'category': 'climate', 'icon': 'Wind'},
        {'name': 'Heating', 'category': 'climate', 'icon': 'Flame'},
        
        # Appliances
        {'name': 'Dishwasher', 'category': 'appliances', 'icon': 'Droplets'},
        {'name': 'Refrigerator', 'category': 'appliances', 'icon': 'Box'},
        {'name': 'Washer/Dryer', 'category': 'appliances', 'icon': 'WashingMachine'},
        
        # Interior
        {'name': 'Hardwood Floors', 'category': 'interior', 'icon': 'Square'},
        {'name': 'Walk-in Closet', 'category': 'interior', 'icon': 'Door'},
        {'name': 'Balcony', 'category': 'interior', 'icon': 'Home'},
        
        # Policies
        {'name': 'Pet Friendly', 'category': 'policies', 'icon': 'Dog'},
        {'name': 'Smoking Allowed', 'category': 'policies', 'icon': 'Cigarette'},
        {'name': 'Utilities Included', 'category': 'policies', 'icon': 'Lightbulb'},
    ]

    for amenity_data in INITIAL_AMENITIES:
        Amenity.objects.create(**amenity_data)

    for feature_data in INITIAL_FEATURES:
        PropertyFeature.objects.create(**feature_data)

def remove_initial_data(apps, schema_editor):
    Amenity = apps.get_model('properties', 'Amenity')
    PropertyFeature = apps.get_model('properties', 'PropertyFeature')
    Amenity.objects.all().delete()
    PropertyFeature.objects.all().delete()




class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_amenity_propertyfeature_unit_parking_spots_and_more'),
    ]

    operations = [
        migrations.RunPython(add_initial_data, remove_initial_data),
    ]

