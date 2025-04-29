from django.db import models
from django.core.exceptions import ValidationError
from myrealestate.common.models import BaseModel, CurrencyField
from .enums import PropertyType, PurchaseType

class PropertyPurchase(BaseModel):
    """Records the purchase details of a property with South African-specific fields"""
    # Link to the property
    property_type = models.CharField(max_length=2, choices=PropertyType.choices)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="property_purchases")
    
    # Basic purchase information
    purchase_date = models.DateField()
    purchase_price = CurrencyField(help_text="Purchase price")
    purchase_type = models.CharField(max_length=2, choices=PurchaseType.choices, default=PurchaseType.BUSINESS)
    
    # South African-specific costs
    transfer_duty = CurrencyField(help_text="Transfer duty paid to SARS")
    is_vat_applicable = models.BooleanField(default=False, help_text="If true, VAT was paid instead of transfer duty")
    vat_amount = CurrencyField(help_text="VAT amount if applicable (usually 15% of purchase price)")
    
    # Legal and registration costs
    bond_registration_cost = CurrencyField(help_text="Cost to register the bond")
    transfer_cost = CurrencyField(help_text="Cost to transfer the property")
    conveyancing_fees = CurrencyField(help_text="Legal fees for conveyancing")
    deeds_office_fees = CurrencyField(help_text="Fees paid to the Deeds Office")
    
    # Financing information
    down_payment = CurrencyField(help_text="Initial payment/deposit")
    financing_amount = CurrencyField(help_text="Amount financed (bond)")
    bond_registration_fee = CurrencyField(help_text="Fee to register the bond")
    bond_initiation_fee = CurrencyField(help_text="Bank's initiation fee for the bond")
    
    # Additional costs
    municipal_rates_clearance = CurrencyField(help_text="Municipal rates clearance certificate fee")
    levy_clearance = CurrencyField(help_text="Levy clearance certificate fee (for sectional title)")
    occupational_rent = CurrencyField(help_text="Occupational rent if applicable")
    initial_repair_costs = CurrencyField(help_text="Initial repairs or renovations")
    
    purchase_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"Purchase of {self.get_property_type_display()} #{self.property_id} on {self.purchase_date}"
    
    def clean(self):
        # Transfer duty and VAT validation
        if self.is_vat_applicable and self.transfer_duty.amount > 0:
            raise ValidationError("Either transfer duty OR VAT should be applicable, not both")
        
        # Down payment + financing amount validation
        total_funds = self.down_payment.amount + self.financing_amount.amount
        if not self.is_vat_applicable and abs(total_funds - self.purchase_price.amount) > 1:  # Allow for rounding
            raise ValidationError("Down payment plus financing amount must equal the purchase price")
    
    @property
    def total_acquisition_cost(self):
        """Calculate the total cost of acquiring the property"""
        from djmoney.money import Money
        
        total = (
            self.purchase_price.amount +
            self.transfer_duty.amount +
            self.vat_amount.amount +
            self.bond_registration_cost.amount +
            self.transfer_cost.amount +
            self.conveyancing_fees.amount +
            self.deeds_office_fees.amount +
            self.bond_registration_fee.amount +
            self.bond_initiation_fee.amount +
            self.municipal_rates_clearance.amount +
            self.levy_clearance.amount +
            self.occupational_rent.amount +
            self.initial_repair_costs.amount
        )
        
        return Money(total, 'ZAR')
    
    @property
    def total_transfer_cost(self):
        """Calculate the total transfer-related costs"""
        from djmoney.money import Money
        
        total = (
            self.transfer_duty.amount +
            self.vat_amount.amount +
            self.transfer_cost.amount +
            self.conveyancing_fees.amount +
            self.deeds_office_fees.amount +
            self.municipal_rates_clearance.amount +
            self.levy_clearance.amount
        )
        
        return Money(total, 'ZAR')
    
    @property
    def total_bond_cost(self):
        """Calculate the total bond-related costs"""
        from djmoney.money import Money
        
        total = (
            self.bond_registration_cost.amount +
            self.bond_registration_fee.amount +
            self.bond_initiation_fee.amount
        )
        
        return Money(total, 'ZAR')
    
    def get_property_object(self):
        """Get the actual property object"""
        from myrealestate.properties.models import Estate, Building, Unit
        
        if self.property_type == PropertyType.ESTATE:
            return Estate.objects.filter(id=self.property_id).first()
        elif self.property_type == PropertyType.BUILDING:
            return Building.objects.filter(id=self.property_id).first()
        elif self.property_type == PropertyType.UNIT:
            return Unit.objects.filter(id=self.property_id).first()
        return None
