from django import forms
from django.utils import timezone
from myrealestate.common.forms import BaseModelForm, BasePatchForm
from myrealestate.properties.models import Estate, Building, Unit, Amenity, PropertyFeature
from myrealestate.finances.models import (
    PropertyPurchase, PropertyBond, MunicipalAccount, BodyCorporate, 
    FinancialCategory, FinancialTransaction
)


class PropertyPurchaseForm(BaseModelForm):
    """Form for recording property purchases"""
    
    class Meta:
        model = PropertyPurchase
        fields = [
            'purchase_date', 'purchase_price', 'purchase_type', 
            'transfer_duty', 'is_vat_applicable', 'vat_amount',
            'bond_registration_cost', 'transfer_cost', 'conveyancing_fees',
            'deeds_office_fees', 'down_payment', 'financing_amount',
            'bond_registration_fee', 'bond_initiation_fee', 'municipal_rates_clearance',
            'levy_clearance', 'occupational_rent', 'initial_repair_costs',
            'purchase_notes'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'purchase_notes': forms.Textarea(attrs={'rows': 3}),
            'is_vat_applicable': forms.CheckboxInput(),
        }
        
    def __init__(self, *args, **kwargs):
        self.property_obj = kwargs.pop('property_obj', None)
        super().__init__(*args, **kwargs)
        
        # Set initial date to today
        self.fields['purchase_date'].initial = timezone.now().date()
        
        # Add help text
        self.fields['is_vat_applicable'].help_text = "Check if VAT was paid instead of transfer duty"
        self.fields['transfer_duty'].help_text = "Properties under R1,100,000 are exempt from transfer duty"
        self.fields['down_payment'].help_text = "The amount you paid upfront"
        self.fields['financing_amount'].help_text = "The amount financed through a bond/mortgage"
        
        # Simplify form for users who don't know all details
        self.fields['transfer_duty'].required = False
        self.fields['vat_amount'].required = False
        self.fields['bond_registration_cost'].required = False
        self.fields['transfer_cost'].required = False
        self.fields['conveyancing_fees'].required = False
        self.fields['deeds_office_fees'].required = False
        self.fields['bond_registration_fee'].required = False
        self.fields['bond_initiation_fee'].required = False
        self.fields['municipal_rates_clearance'].required = False
        self.fields['levy_clearance'].required = False
        self.fields['occupational_rent'].required = False
        self.fields['initial_repair_costs'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        is_vat_applicable = cleaned_data.get('is_vat_applicable')
        transfer_duty = cleaned_data.get('transfer_duty')
        vat_amount = cleaned_data.get('vat_amount')
        
        # Check mutually exclusive transfer duty and VAT
        if is_vat_applicable and transfer_duty and transfer_duty.amount > 0:
            self.add_error('transfer_duty', 
                          "Either transfer duty OR VAT should be applicable, not both")
        
        # Check VAT amount is provided when VAT is applicable
        if is_vat_applicable and (not vat_amount or vat_amount.amount == 0):
            self.add_error('vat_amount', 
                          "VAT amount is required when 'VAT applicable' is checked")
        
        # Verify financing makes sense
        purchase_price = cleaned_data.get('purchase_price')
        down_payment = cleaned_data.get('down_payment')
        financing_amount = cleaned_data.get('financing_amount')
        
        if purchase_price and down_payment and financing_amount:
            total_funds = down_payment.amount + financing_amount.amount
            if abs(total_funds - purchase_price.amount) > 1:  # Allow for small rounding errors
                self.add_error('financing_amount', 
                              "Down payment plus financing amount must equal the purchase price")
        
        # Set property information if provided
        if self.property_obj:
            if hasattr(self.property_obj, 'estate'):
                cleaned_data['property_type'] = 'estate'
                cleaned_data['property_id'] = self.property_obj.id
            elif hasattr(self.property_obj, 'building'):
                cleaned_data['property_type'] = 'building'
                cleaned_data['property_id'] = self.property_obj.id
            elif hasattr(self.property_obj, 'unit'):
                cleaned_data['property_type'] = 'unit'
                cleaned_data['property_id'] = self.property_obj.id
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set property type and ID if a property object was provided
        if self.property_obj:
            property_type = self.property_obj.__class__.__name__.lower()
            instance.property_type = property_type
            instance.property_id = self.property_obj.id
        
        if commit:
            instance.save()
        
        return instance


class PropertyBondForm(BaseModelForm):
    """Form for recording property bond/mortgage details"""
    
    class Meta:
        model = PropertyBond
        fields = [
            'lender', 'account_number', 'bond_amount', 'start_date', 'term_years',
            'interest_rate_type', 'current_interest_rate', 'prime_linked', 'prime_rate_margin',
            'monthly_payment', 'payment_day', 'initiation_fee', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'prime_linked': forms.CheckboxInput(),
        }
        
    def __init__(self, *args, **kwargs):
        self.property_purchase = kwargs.pop('property_purchase', None)
        super().__init__(*args, **kwargs)
        
        # Set initial values
        if self.property_purchase:
            self.fields['bond_amount'].initial = self.property_purchase.financing_amount
            self.fields['start_date'].initial = self.property_purchase.purchase_date
            self.fields['initiation_fee'].initial = self.property_purchase.bond_initiation_fee
        else:
            self.fields['start_date'].initial = timezone.now().date()
        
        # Add help text
        self.fields['term_years'].help_text = "The length of the bond in years (typically 20 or 30)"
        self.fields['prime_linked'].help_text = "Is the interest rate linked to prime?"
        self.fields['prime_rate_margin'].help_text = "Percentage points above/below prime rate"
        self.fields['payment_day'].help_text = "Day of month when payment is due"
        
        # Make certain fields optional
        self.fields['account_number'].required = False
        self.fields['prime_rate_margin'].required = False
        self.fields['notes'].required = False
        self.fields['initiation_fee'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate prime rate margin is provided when prime linked
        prime_linked = cleaned_data.get('prime_linked')
        prime_rate_margin = cleaned_data.get('prime_rate_margin')
        
        if prime_linked and prime_rate_margin is None:
            self.add_error('prime_rate_margin', 
                          "Prime rate margin is required when linked to prime rate")
        
        # Set property purchase if provided
        if self.property_purchase:
            cleaned_data['property_purchase'] = self.property_purchase
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Link to property purchase if provided
        if self.property_purchase and not instance.property_purchase_id:
            instance.property_purchase = self.property_purchase
        
        if commit:
            instance.save()
        
        return instance


class MunicipalAccountForm(BaseModelForm):
    """Form for recording municipal account details"""
    
    class Meta:
        model = MunicipalAccount
        fields = [
            'municipality', 'account_number', 'account_holder',
            'includes_water', 'includes_electricity', 'includes_sewage', 
            'includes_refuse', 'includes_rates',
            'billing_day', 'payment_day', 'municipal_valuation', 
            'valuation_date', 'notes'
        ]
        widgets = {
            'valuation_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'includes_water': forms.CheckboxInput(),
            'includes_electricity': forms.CheckboxInput(),
            'includes_sewage': forms.CheckboxInput(),
            'includes_refuse': forms.CheckboxInput(),
            'includes_rates': forms.CheckboxInput(),
        }
        
    def __init__(self, *args, **kwargs):
        self.property_obj = kwargs.pop('property_obj', None)
        super().__init__(*args, **kwargs)
        
        # Set initial values
        self.fields['valuation_date'].initial = timezone.now().date()
        
        # Add help text
        self.fields['billing_day'].help_text = "Day of month when bill is typically issued"
        self.fields['payment_day'].help_text = "Day of month when payment is due"
        
        # Make certain fields optional
        self.fields['municipal_valuation'].required = False
        self.fields['valuation_date'].required = False
        self.fields['notes'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Set property information if provided
        if self.property_obj:
            property_type = self.property_obj.__class__.__name__.lower()
            cleaned_data['property_type'] = property_type
            cleaned_data['property_id'] = self.property_obj.id
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set property type and ID if a property object was provided
        if self.property_obj:
            property_type = self.property_obj.__class__.__name__.lower()
            instance.property_type = property_type
            instance.property_id = self.property_obj.id
        
        if commit:
            instance.save()
        
        return instance


class BodyCorporateForm(BaseModelForm):
    """Form for recording body corporate (HOA) details"""
    
    class Meta:
        model = BodyCorporate
        fields = [
            'name', 'contact_person', 'contact_email', 'contact_phone',
            'monthly_levy', 'special_levy', 'special_levy_end_date', 
            'levy_increase_month', 'payment_day', 'account_number', 'notes'
        ]
        widgets = {
            'special_levy_end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        self.property_obj = kwargs.pop('property_obj', None)
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['levy_increase_month'].help_text = "Month when levies typically increase"
        self.fields['payment_day'].help_text = "Day of month when payment is due"
        
        # Make certain fields optional
        self.fields['contact_person'].required = False
        self.fields['contact_email'].required = False
        self.fields['contact_phone'].required = False
        self.fields['special_levy'].required = False
        self.fields['special_levy_end_date'].required = False
        self.fields['account_number'].required = False
        self.fields['notes'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate special levy end date if special levy provided
        special_levy = cleaned_data.get('special_levy')
        special_levy_end_date = cleaned_data.get('special_levy_end_date')
        
        if special_levy and special_levy.amount > 0 and not special_levy_end_date:
            self.add_error('special_levy_end_date', 
                          "Special levy end date is required when a special levy is specified")
        
        # Set property information if provided
        if self.property_obj:
            property_type = self.property_obj.__class__.__name__.lower()
            cleaned_data['property_type'] = property_type
            cleaned_data['property_id'] = self.property_obj.id
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set property type and ID if a property object was provided
        if self.property_obj:
            property_type = self.property_obj.__class__.__name__.lower()
            instance.property_type = property_type
            instance.property_id = self.property_obj.id
        
        if commit:
            instance.save()
        
        return instance


# Enhanced versions of your existing forms with purchase options

class EstateWithPurchaseForm(BaseModelForm):
    """Form for creating an estate with purchase information"""
    
    include_purchase_info = forms.BooleanField(
        label="Record purchase information",
        required=False,
        initial=False,
        help_text="Check to add purchase details for this property"
    )
    
    class Meta:
        model = Estate
        fields = ['name', 'estate_type', 'managing', 'address', 'amenities']
        labels = {
            'managing': 'Are you managing this estate?',
            'amenities': 'Estate Amenities'
        }
        widgets = {
            'amenities': forms.CheckboxSelectMultiple()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No additional initialization needed for now


class BuildingWithPurchaseForm(BaseModelForm):
    """Form for creating a building with purchase information"""
    
    include_purchase_info = forms.BooleanField(
        label="Record purchase information",
        required=False,
        initial=False,
        help_text="Check to add purchase details for this property"
    )
    
    class Meta:
        model = Building
        fields = ['estate', 'name', 'building_type', 'managing', 'address']
        labels = {'managing': 'Are you managing this building?'}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No additional initialization needed for now


class UnitWithPurchaseForm(BaseModelForm):
    """Form for creating a unit with purchase information"""
    
    include_purchase_info = forms.BooleanField(
        label="Record purchase information",
        required=False,
        initial=False,
        help_text="Check to add purchase details for this property"
    )
    
    class Meta:
        model = Unit
        fields = [
            'building', 'number', 'unit_type',
            'bedrooms', 'bathrooms', 'square_footage',
            'furnished', 'parking_spots', 'base_rent',
            'deposit_amount', 'available_from',
            'amenities', 'features'
        ]
        labels = {
            'furnished': 'Is the unit furnished?',
            'amenities': 'Unit Amenities',
            'features': 'Unit Features'
        }
        widgets = {
            'amenities': forms.CheckboxSelectMultiple(),
            'features': forms.CheckboxSelectMultiple(),
            'available_from': forms.DateInput(attrs={'type': 'date'})
        }