from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from myrealestate.properties.forms import (
    EstateForm, EstatePatchForm,
    BuildingForm, BuildingPatchForm,
    UnitForm, UnitPatchForm
)
from myrealestate.properties.models import (
    Estate, Building, Unit, Amenity, PropertyFeature,
    EstateTypeEnums, BuildingTypeEnums, UnitTypeEnums
)
from myrealestate.companies.models import Company
from myrealestate.accounts.tests.factories import UserFactory


class EstateFormTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.amenity1 = Amenity.objects.create(name="Swimming Pool", category="Recreation")
        self.amenity2 = Amenity.objects.create(name="Gym", category="Fitness")
        
        # Valid form data
        self.valid_data = {
            'name': 'Test Estate',
            'estate_type': EstateTypeEnums.RESIDENTIAL,
            'managing': True,
            'address': '123 Test St',
            'amenities': [self.amenity1.id, self.amenity2.id]
        }
        
    def test_estate_form_valid(self):
        """Test that EstateForm validates with correct data"""
        form = EstateForm(data=self.valid_data)
        form.instance.company = self.company
        
        self.assertTrue(form.is_valid())
        estate = form.save()
        
        self.assertEqual(estate.name, 'Test Estate')
        self.assertEqual(estate.estate_type, EstateTypeEnums.RESIDENTIAL)
        self.assertTrue(estate.managing)
        self.assertEqual(estate.address, '123 Test St')
        self.assertEqual(estate.amenities.count(), 2)
        
    def test_estate_form_invalid(self):
        """Test that EstateForm validates properly with incorrect data"""
        # Missing required field
        invalid_data = self.valid_data.copy()
        invalid_data.pop('name')
        
        form = EstateForm(data=invalid_data)
        form.instance.company = self.company
        
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
    def test_estate_patch_form(self):
        """Test that EstatePatchForm works for partial updates"""
        # Create an estate first
        estate = Estate.objects.create(
            name='Original Estate',
            estate_type=EstateTypeEnums.RESIDENTIAL,
            managing=True,
            address='Original Address',
            company=self.company
        )
        estate.amenities.add(self.amenity1)
        
        # Update only the name
        patch_data = {
            '_method': 'PATCH',
            'name': 'Updated Estate Name'
        }
        
        form = EstatePatchForm(data=patch_data, instance=estate, company=self.company)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        updated_estate = form.save()
        updated_estate.refresh_from_db()
        
        # Check that only name was updated
        self.assertEqual(updated_estate.name, 'Updated Estate Name')
        self.assertEqual(updated_estate.address, 'Original Address')  # Unchanged
        self.assertEqual(updated_estate.estate_type, EstateTypeEnums.RESIDENTIAL)  # Unchanged
        self.assertTrue(updated_estate.managing)  # Unchanged
        self.assertEqual(updated_estate.amenities.count(), 1)  # Unchanged
        
    def test_form_widgets(self):
        """Test that the form has the correct widgets"""
        form = EstateForm()
        
        # Check that amenities uses CheckboxSelectMultiple
        self.assertEqual(form.fields['amenities'].widget.__class__.__name__, 'CheckboxSelectMultiple')
        
        # Check labels
        self.assertEqual(form.fields['managing'].label, 'Are you managing this estate?')
        self.assertEqual(form.fields['amenities'].label, 'Estate Amenities')


class BuildingFormTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.estate = Estate.objects.create(
            name="Test Estate",
            company=self.company,
            estate_type=EstateTypeEnums.RESIDENTIAL
        )
        
        # Valid form data
        self.valid_data = {
            'estate': self.estate.id,
            'name': 'Test Building',
            'building_type': BuildingTypeEnums.MULTI_UNIT,
            'managing': True,
            'address': '456 Test Ave'
        }
        
    def test_building_form_valid(self):
        """Test that BuildingForm validates with correct data"""
        form = BuildingForm(data=self.valid_data)
        form.instance.company = self.company
        
        self.assertTrue(form.is_valid())
        building = form.save()
        
        self.assertEqual(building.name, 'Test Building')
        self.assertEqual(building.building_type, BuildingTypeEnums.MULTI_UNIT)
        self.assertTrue(building.managing)
        self.assertEqual(building.address, '456 Test Ave')
        self.assertEqual(building.estate, self.estate)
        
    def test_building_form_invalid(self):
        """Test that BuildingForm validates properly with incorrect data"""
        # Missing required field
        invalid_data = self.valid_data.copy()
        invalid_data.pop('name')
        
        form = BuildingForm(data=invalid_data)
        form.instance.company = self.company
        
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
    def test_building_patch_form(self):
        """Test that BuildingPatchForm works for partial updates"""
        # Create a building first
        building = Building.objects.create(
            estate=self.estate,
            name='Original Building',
            building_type=BuildingTypeEnums.MULTI_UNIT,
            managing=True,
            address='Original Address',
            company=self.company
        )
        
        # Update only the name
        patch_data = {
            '_method': 'PATCH',
            'name': 'Updated Building Name'
        }
        
        form = BuildingPatchForm(data=patch_data, instance=building, company=self.company)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        updated_building = form.save()
        updated_building.refresh_from_db()
        
        # Check that only name was updated
        self.assertEqual(updated_building.name, 'Updated Building Name')
        self.assertEqual(updated_building.address, 'Original Address')  # Unchanged
        self.assertEqual(updated_building.building_type, BuildingTypeEnums.MULTI_UNIT)  # Unchanged
        self.assertTrue(updated_building.managing)  # Unchanged
        self.assertEqual(updated_building.estate, self.estate)  # Unchanged
        
    def test_form_labels(self):
        """Test that the form has the correct labels"""
        form = BuildingForm()
        
        # Check labels
        self.assertEqual(form.fields['managing'].label, 'Are you managing this building?')


class UnitFormTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.estate = Estate.objects.create(
            name="Test Estate",
            company=self.company
        )
        self.building = Building.objects.create(
            estate=self.estate,
            name="Test Building",
            building_type=BuildingTypeEnums.MULTI_UNIT,
            company=self.company
        )
        self.amenity = Amenity.objects.create(name="Air Conditioning", category="Comfort")
        self.feature = PropertyFeature.objects.create(name="Hardwood Floors", category="Interior")
        
        # Valid form data
        self.valid_data = {
            'building': self.building.id,
            'number': '101',
            'unit_type': UnitTypeEnums.APARTMENT,
            'bedrooms': 2,
            'bathrooms': 1.5,
            'square_footage': 800,
            'furnished': True,
            'parking_spots': 1,
            'base_rent': 1200,
            'deposit_amount': 1200,
            'available_from': timezone.now().date(),
            'amenities': [self.amenity.id],
            'features': [self.feature.id]
        }
        
    def test_unit_form_valid(self):
        """Test that UnitForm validates with correct data"""
        form = UnitForm(data=self.valid_data)
        form.instance.company = self.company
        
        self.assertTrue(form.is_valid())
        unit = form.save()
        
        self.assertEqual(unit.number, '101')
        self.assertEqual(unit.unit_type, UnitTypeEnums.APARTMENT)
        self.assertEqual(unit.bedrooms, 2)
        self.assertEqual(unit.bathrooms, 1.5)
        self.assertEqual(unit.square_footage, 800)
        self.assertTrue(unit.furnished)
        self.assertEqual(unit.parking_spots, 1)
        self.assertEqual(unit.base_rent, 1200)
        self.assertEqual(unit.deposit_amount, 1200)
        self.assertEqual(unit.building, self.building)
        self.assertEqual(unit.amenities.count(), 1)
        self.assertEqual(unit.features.count(), 1)
        
    def test_unit_form_invalid(self):
        """Test that UnitForm validates properly with incorrect data"""
        # Missing required field
        invalid_data = self.valid_data.copy()
        invalid_data.pop('number')
        
        form = UnitForm(data=invalid_data)
        form.instance.company = self.company
        
        self.assertFalse(form.is_valid())
        self.assertIn('number', form.errors)
        
        # Invalid data type
        invalid_data = self.valid_data.copy()
        invalid_data['bedrooms'] = 'not a number'
        
        form = UnitForm(data=invalid_data)
        form.instance.company = self.company
        
        self.assertFalse(form.is_valid())
        self.assertIn('bedrooms', form.errors)
        
    def test_unit_patch_form(self):
        """Test that UnitPatchForm works for partial updates"""
        # Create a unit first
        unit = Unit.objects.create(
            building=self.building,
            number='101',
            unit_type=UnitTypeEnums.APARTMENT,
            bedrooms=1,
            bathrooms=1,
            square_footage=700,
            base_rent=1000,
            company=self.company
        )
        unit.amenities.add(self.amenity)
        unit.features.add(self.feature)
        
        # Update only some fields
        patch_data = {
            '_method': 'PATCH',
            'bedrooms': 2,
            'base_rent': 1200
        }
        
        form = UnitPatchForm(data=patch_data, instance=unit, company=self.company)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        updated_unit = form.save()
        updated_unit.refresh_from_db()
        
        # Check that only specified fields were updated
        self.assertEqual(updated_unit.bedrooms, 2)  # Updated
        self.assertEqual(updated_unit.base_rent, 1200)  # Updated
        self.assertEqual(updated_unit.number, '101')  # Unchanged
        self.assertEqual(updated_unit.square_footage, 700)  # Unchanged
        self.assertEqual(updated_unit.bathrooms, 1)  # Unchanged
        self.assertEqual(updated_unit.unit_type, UnitTypeEnums.APARTMENT)  # Unchanged
        self.assertEqual(updated_unit.amenities.count(), 1)  # Unchanged
        self.assertEqual(updated_unit.features.count(), 1)  # Unchanged
        
    def test_form_widgets(self):
        """Test that the form has the correct widgets"""
        form = UnitForm()
        
        # Check widgets
        self.assertEqual(form.fields['amenities'].widget.__class__.__name__, 'CheckboxSelectMultiple')
        self.assertEqual(form.fields['features'].widget.__class__.__name__, 'CheckboxSelectMultiple')
        self.assertEqual(form.fields['available_from'].widget.__class__.__name__, 'DateInput')
        self.assertEqual(form.fields['available_from'].widget.attrs['type'], 'date')
        
        # Check labels
        self.assertEqual(form.fields['furnished'].label, 'Is the unit furnished?')
        self.assertEqual(form.fields['amenities'].label, 'Unit Amenities')
        self.assertEqual(form.fields['features'].label, 'Unit Features')