from django.db import models
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from myrealestate.common.models import BaseModel
from decimal import Decimal
import uuid
from myrealestate.common.models import MoneyField



class FinancialCategory(BaseModel):
    """
    Categories for financial transactions (both income and expenses)
    """
    TYPE_INCOME = 'I'
    TYPE_EXPENSE = 'E'
    TYPE_CHOICES = [
        (TYPE_INCOME, 'Income'),
        (TYPE_EXPENSE, 'Expense'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="financial_categories")
    is_default = models.BooleanField(default=False)
    is_tax_deductible = models.BooleanField(default=False, help_text="Indicates if this expense category is tax deductible")
    
    class Meta:
        unique_together = ('name', 'company', 'category_type')
        ordering = ['name']
        verbose_name_plural = "Financial categories"
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class PropertyPurchase(BaseModel):
    """
    Records the purchase details of a property with South African-specific fields
    """
    PROPERTY_TYPES = [
        ('estate', 'Estate'),
        ('building', 'Building'),
        ('unit', 'Unit'),
    ]
    
    PURCHASE_TYPES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('trust', 'Trust'),
    ]
    
    # Link to the property
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="property_purchases")
    
    # Basic purchase information
    purchase_date = models.DateField()
    purchase_price = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='ZAR', 
        help_text="Purchase price"
    )
    purchase_type = models.CharField(max_length=10, choices=PURCHASE_TYPES, default='business')
    
    # South African-specific costs
    transfer_duty = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Transfer duty paid to SARS"
    )
    is_vat_applicable = models.BooleanField(default=False, help_text="If true, VAT was paid instead of transfer duty")
    vat_amount = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="VAT amount if applicable (usually 15% of purchase price)"
    )
    
    # Legal and registration costs
    bond_registration_cost = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Cost to register the bond"
    )
    transfer_cost = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Cost to transfer the property"
    )
    conveyancing_fees = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Legal fees for conveyancing"
    )
    deeds_office_fees = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Fees paid to the Deeds Office"
    )
    
    # Financing information
    down_payment = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Initial payment/deposit"
    )
    financing_amount = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Amount financed (bond)"
    )
    bond_registration_fee = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Fee to register the bond"
    )
    bond_initiation_fee = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Bank's initiation fee for the bond"
    )
    
    # Additional costs
    municipal_rates_clearance = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Municipal rates clearance certificate fee"
    )
    levy_clearance = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Levy clearance certificate fee (for sectional title)"
    )
    occupational_rent = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Occupational rent if applicable"
    )
    initial_repair_costs = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Initial repairs or renovations"
    )
    
    purchase_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"Purchase of {self.property_type} #{self.property_id} on {self.purchase_date}"
    
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
        
        if self.property_type == 'estate':
            return Estate.objects.filter(id=self.property_id).first()
        elif self.property_type == 'building':
            return Building.objects.filter(id=self.property_id).first()
        elif self.property_type == 'unit':
            return Unit.objects.filter(id=self.property_id).first()
        return None


class PropertyBond(BaseModel):
    """
    Tracks mortgage/bond details for a property
    """
    property_purchase = models.ForeignKey(PropertyPurchase, on_delete=models.CASCADE, related_name="bonds")
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="property_bonds")
    
    # Basic bond information
    lender = models.CharField(max_length=255, help_text="Bank or financial institution")
    account_number = models.CharField(max_length=100, blank=True, null=True)
    bond_amount = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='ZAR', 
        help_text="Total bond amount"
    )
    start_date = models.DateField()
    term_years = models.PositiveIntegerField(help_text="Bond term in years")
    
    # Interest rate details
    interest_rate_type = models.CharField(
        max_length=20,
        choices=[
            ('fixed', 'Fixed Rate'),
            ('variable', 'Variable Rate'),
            ('mixed', 'Mixed Rate'),
        ],
        default='variable'
    )
    current_interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Current annual interest rate (%)",
        validators=[MinValueValidator(0)]
    )
    prime_linked = models.BooleanField(default=True, help_text="Is rate linked to prime rate?")
    prime_rate_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Margin above/below prime rate (%)"
    )
    
    # Payment details
    monthly_payment = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        help_text="Regular monthly bond payment"
    )
    payment_day = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Day of month when payment is due"
    )
    
    # Additional bond information
    is_active = models.BooleanField(default=True)
    initiation_fee = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0
    )
    has_payment_holiday = models.BooleanField(default=False)
    payment_holiday_end_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Bond for {self.property_purchase}: {self.bond_amount} ({self.lender})"
    
    @property
    def end_date(self):
        """Calculate the end date based on start date and term"""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        return self.start_date + relativedelta(years=self.term_years)
    
    @property
    def remaining_term_months(self):
        """Calculate remaining term in months"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        if not self.is_active:
            return 0
            
        today = date.today()
        end_date = self.end_date
        
        if today >= end_date:
            return 0
            
        diff = relativedelta(end_date, today)
        return diff.years * 12 + diff.months


class MunicipalAccount(BaseModel):
    """
    Tracks municipal account details for a property
    """
    PROPERTY_TYPES = [
        ('estate', 'Estate'),
        ('building', 'Building'),
        ('unit', 'Unit'),
    ]
    
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="municipal_accounts")
    
    # Municipal account details
    municipality = models.CharField(max_length=255, help_text="Name of municipality")
    account_number = models.CharField(max_length=100)
    account_holder = models.CharField(max_length=255)
    
    # Service details
    includes_water = models.BooleanField(default=True)
    includes_electricity = models.BooleanField(default=True)
    includes_sewage = models.BooleanField(default=True)
    includes_refuse = models.BooleanField(default=True)
    includes_rates = models.BooleanField(default=True)
    
    # Billing details
    billing_day = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Day of month when bill is typically issued"
    )
    payment_day = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Day of month when payment is due"
    )
    
    # Property valuation for rates
    municipal_valuation = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='ZAR', 
        null=True, 
        blank=True, 
        help_text="Municipal valuation for rates calculation"
    )
    valuation_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['municipality', 'account_number']
        
    def __str__(self):
        return f"Municipal Account: {self.account_number} ({self.municipality})"
    
    def get_property_object(self):
        """Get the actual property object"""
        from myrealestate.properties.models import Estate, Building, Unit
        
        if self.property_type == 'estate':
            return Estate.objects.filter(id=self.property_id).first()
        elif self.property_type == 'building':
            return Building.objects.filter(id=self.property_id).first()
        elif self.property_type == 'unit':
            return Unit.objects.filter(id=self.property_id).first()
        return None


class BodyCorporate(BaseModel):
    """
    Tracks body corporate (HOA) details for sectional title properties
    """
    PROPERTY_TYPES = [
        ('estate', 'Estate'),
        ('building', 'Building'),
        ('unit', 'Unit'),
    ]
    
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="body_corporates")
    
    # Body corporate details
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Levy details
    monthly_levy = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        help_text="Regular monthly levy amount"
    )
    special_levy = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="Any special levy currently in effect"
    )
    special_levy_end_date = models.DateField(null=True, blank=True)
    levy_increase_month = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 13)],
        default=1,
        help_text="Month when levies typically increase"
    )
    
    # Payment details
    payment_day = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Day of month when payment is due"
    )
    account_number = models.CharField(max_length=100, blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Body corporates"
        
    def __str__(self):
        return f"Body Corporate: {self.name}"
    
    def get_property_object(self):
        """Get the actual property object"""
        from myrealestate.properties.models import Estate, Building, Unit
        
        if self.property_type == 'estate':
            return Estate.objects.filter(id=self.property_id).first()
        elif self.property_type == 'building':
            return Building.objects.filter(id=self.property_id).first()
        elif self.property_type == 'unit':
            return Unit.objects.filter(id=self.property_id).first()
        return None


class FinancialTransaction(BaseModel):
    """
    Base model for financial transactions
    """
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    PROPERTY_TYPES = [
        ('estate', 'Estate'),
        ('building', 'Building'),
        ('unit', 'Unit'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('electronic', 'Electronic Payment'),
        ('debit_order', 'Debit Order'),
        ('other', 'Other'),
    ]
    
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    
    # Link to property in property hierarchy
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="financial_transactions")
    
    # Financial details
    amount = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        help_text="Transaction amount"
    )
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name="transactions")
    
    # VAT information (important for SA businesses)
    includes_vat = models.BooleanField(default=True, help_text="Does this amount include VAT?")
    vat_amount = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="VAT portion of the amount"
    )
    
    # Transaction metadata
    date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # For expenses
    vendor = models.CharField(max_length=255, blank=True, null=True)
    vendor_vat_number = models.CharField(max_length=20, blank=True, null=True, help_text="VAT registration number of vendor")
    
    # For income - can link to tenant
    tenant = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_transactions")
    
    # Links to specific account types
    municipal_account = models.ForeignKey(MunicipalAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    body_corporate = models.ForeignKey(BodyCorporate, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    property_bond = models.ForeignKey(PropertyBond, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Tax information
    is_tax_deductible = models.BooleanField(default=False, help_text="Is this expense tax deductible?")
    tax_year = models.IntegerField(null=True, blank=True, help_text="Tax year this transaction belongs to")
    
    # Receipt or invoice attachment
    attachment = models.FileField(upload_to='financial/attachments/%Y/%m/', null=True, blank=True)
    
    # Status tracking
    is_paid = models.BooleanField(default=True)
    payment_date = models.DateField(null=True, blank=True, help_text="Date when payment was made or received")
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['property_type', 'property_id']),
            models.Index(fields=['date']),
            models.Index(fields=['is_paid']),
            models.Index(fields=['tax_year']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} on {self.date}"
    
    def clean(self):
        # Ensure category type matches transaction type
        if self.transaction_type == 'income' and self.category.category_type != FinancialCategory.TYPE_INCOME:
            raise ValidationError("Category must be an income category for income transactions")
        if self.transaction_type == 'expense' and self.category.category_type != FinancialCategory.TYPE_EXPENSE:
            raise ValidationError("Category must be an expense category for expense transactions")
        
        # Set tax year if not provided
        if not self.tax_year:
            # South African tax year runs from March to February
            tax_year_start_month = 3  # March
            date_year = self.date.year
            date_month = self.date.month
            
            if date_month < tax_year_start_month:
                self.tax_year = date_year - 1
            else:
                self.tax_year = date_year
    
    def get_property_object(self):
        """Get the actual property object"""
        from myrealestate.properties.models import Estate, Building, Unit
        
        if self.property_type == 'estate':
            return Estate.objects.filter(id=self.property_id).first()
        elif self.property_type == 'building':
            return Building.objects.filter(id=self.property_id).first()
        elif self.property_type == 'unit':
            return Unit.objects.filter(id=self.property_id).first()
        return None
    
    @classmethod
    def get_transactions_for_property(cls, property_obj, start_date=None, end_date=None):
        """
        Get all transactions for a specific property
        """
        property_type = property_obj.__class__.__name__.lower()
        property_id = property_obj.id
        
        query = cls.objects.filter(property_type=property_type, property_id=property_id)
        
        if start_date:
            query = query.filter(date__gte=start_date)
        if end_date:
            query = query.filter(date__lte=end_date)
            
        return query
    
    @classmethod
    def get_income_for_property(cls, property_obj, start_date=None, end_date=None):
        """
        Get income transactions for a specific property
        """
        return cls.get_transactions_for_property(
            property_obj, start_date, end_date
        ).filter(transaction_type='income')
    
    @classmethod
    def get_expenses_for_property(cls, property_obj, start_date=None, end_date=None):
        """
        Get expense transactions for a specific property
        """
        return cls.get_transactions_for_property(
            property_obj, start_date, end_date
        ).filter(transaction_type='expense')
    
    @property
    def is_tax_deductible_auto(self):
        """
        Automatically determine if transaction is tax deductible based on category
        """
        if self.transaction_type == 'expense' and self.category:
            return self.category.is_tax_deductible
        return False


class RecurringTransaction(BaseModel):
    """
    Template for recurring financial transactions
    """
    RECURRENCE_FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Every Two Weeks'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannually', 'Semi-Annually'),
        ('annually', 'Annually'),
    ]
    
    PROPERTY_TYPES = [
        ('estate', 'Estate'),
        ('building', 'Building'),
        ('unit', 'Unit'),
    ]
    
    transaction_type = models.CharField(max_length=10, choices=FinancialTransaction.TRANSACTION_TYPES)
    
    # Link to property
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES)
    property_id = models.IntegerField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="recurring_transactions")
    
    # Financial details
    amount = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        help_text="Amount"
    )
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name="recurring_transactions")
    
    # VAT information
    includes_vat = models.BooleanField(default=True, help_text="Does this amount include VAT?")
    vat_amount = MoneyField(
        max_digits=12, 
        decimal_places=2, 
        default_currency='ZAR', 
        default=0, 
        help_text="VAT portion of the amount"
    )
    
    # Recurrence details
    frequency = models.CharField(max_length=15, choices=RECURRENCE_FREQUENCIES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField()
    
    # For expenses
    vendor = models.CharField(max_length=255, blank=True, null=True)
    vendor_vat_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Links to specific account types
    municipal_account = models.ForeignKey(MunicipalAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="recurring_transactions")
    body_corporate = models.ForeignKey(BodyCorporate, on_delete=models.SET_NULL, null=True, blank=True, related_name="recurring_transactions")
    property_bond = models.ForeignKey(PropertyBond, on_delete=models.SET_NULL, null=True, blank=True, related_name="recurring_transactions")
    
    # For tenant-related transactions
    tenant = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name="tenant_recurring_transactions")
    
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Tax information
    is_tax_deductible = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['next_due_date']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} ({self.get_frequency_display()})"
    
    def clean(self):
        # Ensure category type matches transaction type
        if self.transaction_type == 'income' and self.category.category_type != FinancialCategory.TYPE_INCOME:
            raise ValidationError("Category must be an income category for income transactions")
        if self.transaction_type == 'expense' and self.category.category_type != FinancialCategory.TYPE_EXPENSE:
            raise ValidationError("Category must be an expense category for expense transactions")
    
    def calculate_next_due_date(self):
        """
        Calculate the next due date based on frequency and current next_due_date
        """
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        current = self.next_due_date
        
        if self.frequency == 'daily':
            return current + timedelta(days=1)
        elif self.frequency == 'semiannually':
            return current + relativedelta(months=6)
        elif self.frequency == 'annually':
            return current + relativedelta(years=1)
        return current
    
    def create_transaction(self):
        """
        Create a financial transaction based on this recurring template
        """
        # Determine tax year
        tax_year_start_month = 3  # March
        date_year = self.next_due_date.year
        date_month = self.next_due_date.month
        
        if date_month < tax_year_start_month:
            tax_year = date_year - 1
        else:
            tax_year = date_year
        
        transaction = FinancialTransaction(
            transaction_type=self.transaction_type,
            property_type=self.property_type,
            property_id=self.property_id,
            company=self.company,
            amount=self.amount,
            category=self.category,
            date=self.next_due_date,
            tenant=self.tenant,
            vendor=self.vendor,
            vendor_vat_number=self.vendor_vat_number,
            includes_vat=self.includes_vat,
            vat_amount=self.vat_amount,
            is_tax_deductible=self.is_tax_deductible,
            tax_year=tax_year,
            municipal_account=self.municipal_account,
            body_corporate=self.body_corporate,
            property_bond=self.property_bond,
            description=self.description,
            notes=f"Auto-generated from recurring transaction: {self.pk}"
        )
        transaction.save()
        
        # Update next due date
        self.next_due_date = self.calculate_next_due_date()
        
        # If end date is set and we've passed it, deactivate
        if self.end_date and self.next_due_date > self.end_date:
            self.is_active = False
            
        self.save()
        
        return transaction

'''
# Create default financial categories for South African property management
def create_default_financial_categories(company):
    """
    Creates default financial categories for a new company
    """
    # Income categories
    income_categories = [
        {"name": "Rental Income", "description": "Regular rental income from tenants"},
        {"name": "Parking Income", "description": "Income from parking spots or garages"},
        {"name": "Deposit Income", "description": "Income from tenant deposits"},
        {"name": "Utility Recovery", "description": "Recovery of utility costs from tenants"},
        {"name": "Late Fee Income", "description": "Income from late payment fees"},
        {"name": "Interest Income", "description": "Interest earned on deposits or investments"},
    ]
    
    # Expense categories - South African specific
    expense_categories = [
        {"name": "Municipal Rates", "description": "Property rates paid to municipality", "is_tax_deductible": True},
        {"name": "Water & Sanitation", "description": "Water and sewage charges", "is_tax_deductible": True},
        {"name": "Electricity", "description": "Electricity charges", "is_tax_deductible": True},
        {"name": "Body Corporate Levy", "description": "Monthly levies paid to body corporate", "is_tax_deductible": True},
        {"name": "Special Levy", "description": "Special levies for improvements or repairs", "is_tax_deductible": True},
        {"name": "Bond Repayment", "description": "Monthly bond/mortgage repayments"},
        {"name": "Bond Interest", "description": "Interest portion of bond payment", "is_tax_deductible": True},
        {"name": "Insurance", "description": "Property and building insurance", "is_tax_deductible": True},
        {"name": "Maintenance", "description": "Regular property maintenance", "is_tax_deductible": True},
        {"name": "Repairs", "description": "Property repairs", "is_tax_deductible": True},
        {"name": "Management Fees", "description": "Property management fees", "is_tax_deductible": True},
        {"name": "Legal Fees", "description": "Legal expenses related to property", "is_tax_deductible": True},
        {"name": "Accounting Fees", "description": "Accounting and tax preparation fees", "is_tax_deductible": True},
        {"name": "Security", "description": "Security services and equipment", "is_tax_deductible": True},
        {"name": "Refuse Removal", "description": "Garbage and waste removal", "is_tax_deductible": True},
        {"name": "Cleaning", "description": "Cleaning services", "is_tax_deductible": True},
        {"name": "Gardening", "description": "Garden and landscaping services", "is_tax_deductible": True},
        {"name": "Pest Control", "description": "Pest control services", "is_tax_deductible": True},
        {"name": "Advertising", "description": "Property advertising and marketing", "is_tax_deductible": True},
        {"name": "Travel", "description": "Travel expenses related to property", "is_tax_deductible": True},
        {"name": "Estate Agent Commission", "description": "Commission paid to rental agents", "is_tax_deductible": True},
        {"name": "Depreciation", "description": "Depreciation of property assets", "is_tax_deductible": True},
    ]
    
    # Create income categories
    for category_data in income_categories:
        FinancialCategory.objects.get_or_create(
            name=category_data["name"],
            company=company,
            category_type=FinancialCategory.TYPE_INCOME,
            defaults={
                "description": category_data["description"],
                "is_default": True
            }
        )
    
    # Create expense categories
    for category_data in expense_categories:
        is_tax_deductible = category_data.get("is_tax_deductible", False)
        FinancialCategory.objects.get_or_create(
            name=category_data["name"],
            company=company,
            category_type=FinancialCategory.TYPE_EXPENSE,
            defaults={
                "description": category_data["description"],
                "is_default": True,
                "is_tax_deductible": is_tax_deductible
            }
        )'weekly':
            return current + timedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return current + timedelta(weeks=2)
        elif self.frequency == 'monthly':
            return current + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            return current + relativedelta(months=3)
        elif self.frequency ==
'''