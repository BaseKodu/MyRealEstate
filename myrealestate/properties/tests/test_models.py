from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

from myrealestate.properties.models import (
    Estate, Building, Unit, SubUnit, 
    BuildingTypeEnums, UnitTypeEnums, EstateTypeEnums, SubUnitTypeEnums,
    Amenity, PropertyFeature, PropertyImage
)
from myrealestate.companies.tests.factories import CompanyFactory
from myrealestate.accounts.tests.factories import UserFactory

class EstateModelTest(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.estate = Estate.objects.create(
            name="Test Estate",
            address="123 Test St",
            company=self.company,
            estate_type=EstateTypeEnums.RESIDENTIAL,
            managing=True
        )
    
    def test_estate_creation(self):
        """Test that an estate can be created with proper attributes"""
        self.assertEqual(self.estate.name, "Test Estate")
        self.assertEqual(self.estate.address, "123 Test St")
        self.assertEqual(self.estate.company, self.company)
        self.assertEqual(self.estate.estate_type, EstateTypeEnums.RESIDENTIAL)
        self.assertTrue(self.estate.managing)
        self.assertEqual(str(self.estate), "Test Estate")

    def test_estate_amenities(self):
        """Test that amenities can be added to an estate"""
        amenity = Amenity.objects.create(
            name="Swimming Pool",
            description="Large outdoor pool",
            icon="pool",
            category="Recreation"
        )
        self.estate.amenities.add(amenity, through_defaults={'details': 'Olympic size'})
        
        self.assertEqual(self.estate.amenities.count(), 1)
        self.assertEqual(self.estate.amenity_relations.first().details, 'Olympic size')


class BuildingModelTest(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.estate = Estate.objects.create(
            name="Test Estate",
            company=self.company
        )
        self.multi_building = Building.objects.create(
            estate=self.estate,
            company=self.company,
            name="Multi Unit Building",
            building_type=BuildingTypeEnums.MULTI_UNIT,
            address="456 Test Ave"
        )
        self.single_building = Building.objects.create(
            estate=self.estate,
            company=self.company,
            name="Single Unit Building",
            building_type=BuildingTypeEnums.SINGLE_UNIT,
            address="789 Test Blvd"
        )
    
    def test_building_creation(self):
        """Test that buildings can be created with proper attributes"""
        self.assertEqual(self.multi_building.name, "Multi Unit Building")
        self.assertEqual(self.multi_building.building_type, BuildingTypeEnums.MULTI_UNIT)
        self.assertEqual(self.multi_building.estate, self.estate)
        self.assertEqual(str(self.multi_building), "Multi Unit Building in Test Estate")
        
        # Test standalone property
        self.assertFalse(self.multi_building.is_standalone)
        self.assertTrue(self.single_building.is_standalone)
        
        # Test can_have_multiple_units property
        self.assertTrue(self.multi_building.can_have_multiple_units)
        self.assertFalse(self.single_building.can_have_multiple_units)
    
    def test_single_unit_building_auto_creates_unit(self):
        """Test that a single unit building automatically creates a unit"""
        # The single_building should have auto-created a unit
        self.assertEqual(self.single_building.units.count(), 1)
        unit = self.single_building.units.first()
        self.assertEqual(unit.unit_type, UnitTypeEnums.HOUSE)
        self.assertEqual(unit.number, "1")
    
    def test_building_manager_methods(self):
        """Test the custom manager methods for Building"""
        # Create some units for testing
        Unit.objects.create(
            building=self.multi_building,
            company=self.company,
            number="101",
            unit_type=UnitTypeEnums.APARTMENT,
            is_vacant=True
        )
        Unit.objects.create(
            building=self.multi_building,
            company=self.company,
            number="102",
            unit_type=UnitTypeEnums.APARTMENT,
            is_vacant=False
        )
        
        # Test standalone_houses method
        standalone = Building.objects.standalone_houses()
        self.assertEqual(standalone.count(), 1)
        self.assertEqual(standalone.first(), self.single_building)
        
        # Test apartment_buildings method
        apartments = Building.objects.apartment_buildings()
        self.assertEqual(apartments.count(), 1)
        self.assertEqual(apartments.first(), self.multi_building)
        
        # Test with_vacancy_status method
        buildings_with_status = Building.objects.with_vacancy_status()
        multi_building_status = buildings_with_status.get(id=self.multi_building.id)
        self.assertEqual(multi_building_status.total_units, 2)
        self.assertEqual(multi_building_status.vacant_units, 1)
        
        # Test with_available_units method
        available = Building.objects.with_available_units()
        self.assertEqual(available.count(), 2)  # Both buildings have vacant units


class UnitModelTest(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.estate = Estate.objects.create(
            name="Test Estate",
            company=self.company
        )
        self.multi_building = Building.objects.create(
            estate=self.estate,
            company=self.company,
            name="Multi Unit Building",
            building_type=BuildingTypeEnums.MULTI_UNIT
        )
        self.single_building = Building.objects.create(
            estate=self.estate,
            company=self.company,
            name="Single Unit Building",
            building_type=BuildingTypeEnums.SINGLE_UNIT,
            address="123 House St"
        )
        
        # The single building should have auto-created a unit
        self.house_unit = self.single_building.units.first()
        
        # Create an apartment unit
        self.apartment_unit = Unit.objects.create(
            building=self.multi_building,
            company=self.company,
            number="101",
            unit_type=UnitTypeEnums.APARTMENT,
            is_vacant=True,
            square_footage=800,
            bedrooms=2,
            bathrooms=1.5,
            furnished=True,
            available_from=timezone.now().date(),
            base_rent=1200,
            deposit_amount=1200,
            parking_spots=1
        )
        
        # Create a user for testing
        self.user = UserFactory()
    
    def test_unit_creation(self):
        """Test that units can be created with proper attributes"""
        self.assertEqual(self.apartment_unit.number, "101")
        self.assertEqual(self.apartment_unit.unit_type, UnitTypeEnums.APARTMENT)
        self.assertEqual(self.apartment_unit.building, self.multi_building)
        self.assertTrue(self.apartment_unit.is_vacant)
        self.assertEqual(self.apartment_unit.bedrooms, 2)
        self.assertEqual(self.apartment_unit.bathrooms, 1.5)
        self.assertTrue(self.apartment_unit.furnished)
        self.assertEqual(self.apartment_unit.base_rent, 1200)
        
        # Test string representation
        self.assertEqual(str(self.apartment_unit), "Unit 101 in Multi Unit Building")
        
        # Test is_standalone_house property
        self.assertFalse(self.apartment_unit.is_standalone_house)
        self.assertTrue(self.house_unit.is_standalone_house)
        
        # Test full_address property
        self.assertEqual(self.apartment_unit.full_address, "Unit 101, Multi Unit Building")
        self.assertEqual(self.house_unit.full_address, "123 House St")
    
    def test_unit_validation(self):
        """Test validation rules for units"""
        # Test creating a house in a multi-unit building (should fail)
        with self.assertRaises(ValidationError):
            invalid_unit = Unit(
                building=self.multi_building,
                company=self.company,
                number="102",
                unit_type=UnitTypeEnums.HOUSE
            )
            invalid_unit.clean()
        
        # Test creating an apartment in a single-unit building (should fail)
        with self.assertRaises(ValidationError):
            invalid_unit = Unit(
                building=self.single_building,
                company=self.company,
                number="2",
                unit_type=UnitTypeEnums.APARTMENT
            )
            invalid_unit.clean()
    
    def test_unit_amenities_and_features(self):
        """Test adding amenities and features to a unit"""
        # Create amenity and feature
        amenity = Amenity.objects.create(
            name="Gym",
            icon="fitness",
            category="Fitness"
        )
        feature = PropertyFeature.objects.create(
            name="Hardwood Floors",
            icon="floor",
            category="Interior"
        )
        
        # Add amenity and feature
        self.apartment_unit.add_amenity(amenity, "24/7 access")
        self.apartment_unit.add_feature(feature, "Throughout unit")
        
        # Test they were added correctly
        self.assertEqual(self.apartment_unit.amenities.count(), 1)
        self.assertEqual(self.apartment_unit.features.count(), 1)
        self.assertEqual(self.apartment_unit.amenity_relations.first().details, "24/7 access")
        self.assertEqual(self.apartment_unit.feature_relations.first().details, "Throughout unit")
        
        # Test get_amenities_by_category and get_features_by_category
        amenities_by_category = self.apartment_unit.get_amenities_by_category()
        self.assertIn("Fitness", amenities_by_category)
        
        features_by_category = self.apartment_unit.get_features_by_category()
        self.assertIn("Interior", features_by_category)
    
    def test_unit_manager_methods(self):
        """Test the custom manager methods for Unit"""
        # Create another unit that's not vacant
        occupied_unit = Unit.objects.create(
            building=self.multi_building,
            company=self.company,
            number="102",
            unit_type=UnitTypeEnums.APARTMENT,
            is_vacant=False,
            base_rent=1500,
            main_tenant=self.user
        )
        
        # Test available method
        available_units = Unit.objects.available()
        self.assertEqual(available_units.count(), 1)  # apartment_unit and house_unit
        self.assertIn(self.apartment_unit, available_units)
        self.assertNotIn(occupied_unit, available_units)
        
        # Test standalone_houses method
        houses = Unit.objects.standalone_houses()
        self.assertEqual(houses.count(), 1)
        self.assertEqual(houses.first(), self.house_unit)
        
        # Test apartments method
        apartments = Unit.objects.apartments()
        self.assertEqual(apartments.count(), 2)
        self.assertIn(self.apartment_unit, apartments)
        self.assertIn(occupied_unit, apartments)
        
        # Test in_price_range method
        in_range = Unit.objects.in_price_range(1000, 1300)
        self.assertEqual(in_range.count(), 1)
        self.assertEqual(in_range.first(), self.apartment_unit)


class SubUnitModelTest(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.building = Building.objects.create(
            company=self.company,
            name="Multi Unit Building",
            building_type=BuildingTypeEnums.MULTI_UNIT
        )
        self.unit = Unit.objects.create(
            building=self.building,
            company=self.company,
            number="101",
            unit_type=UnitTypeEnums.APARTMENT,
            bedrooms=3
        )
        
        # Create a subunit
        self.subunit = SubUnit.objects.create(
            parent_unit=self.unit,
            number="101A",
            subunit_type=SubUnitTypeEnums.ROOM,
            is_vacant=True,
            base_rent=500,
            available_from=timezone.now().date()
        )
        
        # Create another subunit that's not vacant
        self.occupied_subunit = SubUnit.objects.create(
            parent_unit=self.unit,
            number="101B",
            subunit_type=SubUnitTypeEnums.ROOM,
            is_vacant=False,
            base_rent=600
        )
        
        # Create a user for testing
        self.user = UserFactory()
    
    def test_subunit_creation(self):
        """Test that subunits can be created with proper attributes"""
        self.assertEqual(self.subunit.number, "101A")
        self.assertEqual(self.subunit.subunit_type, SubUnitTypeEnums.ROOM)
        self.assertEqual(self.subunit.parent_unit, self.unit)
        self.assertTrue(self.subunit.is_vacant)
        self.assertEqual(self.subunit.base_rent, 500)
        
        # Test string representation
        self.assertEqual(str(self.subunit), "SubUnit 101A in Unit 101 in Multi Unit Building")
    
    def test_subunit_manager_methods(self):
        """Test the custom manager methods for SubUnit"""
        # Test available method
        available_subunits = SubUnit.objects.available()
        self.assertEqual(available_subunits.count(), 1)
        self.assertIn(self.subunit, available_subunits)
        self.assertNotIn(self.occupied_subunit, available_subunits)
        
        # Test in_price_range method
        in_range = SubUnit.objects.in_price_range(400, 550)
        self.assertEqual(in_range.count(), 1)
        self.assertEqual(in_range.first(), self.subunit)
        
        # Test with future availability date
        future_subunit = SubUnit.objects.create(
            parent_unit=self.unit,
            number="101C",
            subunit_type=SubUnitTypeEnums.ROOM,
            is_vacant=True,
            base_rent=550,
            available_from=timezone.now().date() + timedelta(days=30)
        )
        
        # Should not be in available units (future date)
        self.assertNotIn(future_subunit, SubUnit.objects.available())