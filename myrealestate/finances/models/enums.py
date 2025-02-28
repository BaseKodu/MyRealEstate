from django.db import models
from django.utils.translation import gettext_lazy as _


# Extracted Enumerators
class CategoryType(models.TextChoices):
    INCOME = 'I', _('Income')
    EXPENSE = 'E', _('Expense')


class PropertyType(models.TextChoices):
    ESTATE = 'es', _('Estate')
    BUILDING = 'bu', _('Building')
    UNIT = 'un', _('Unit')


class PurchaseType(models.TextChoices):
    INDIVIDUAL = 'in', _('Individual')
    BUSINESS = 'bu', _('Business')
    TRUST = 'tr', _('Trust')


class InterestRateType(models.TextChoices):
    FIXED = 'fx', _('Fixed Rate')
    VARIABLE = 'va', _('Variable Rate')
    MIXED = 'mx', _('Mixed Rate')


class TransactionType(models.TextChoices):
    INCOME = 'in', _('Income')
    EXPENSE = 'ex', _('Expense')


class PaymentMethod(models.TextChoices):
    CASH = 'ca', _('Cash')
    CHECK = 'ch', _('Check')
    CREDIT_CARD = 'cc', _('Credit Card')
    BANK_TRANSFER = 'bt', _('Bank Transfer')
    ELECTRONIC = 'ep', _('Electronic Payment')
    DEBIT_ORDER = 'do', _('Debit Order')
    OTHER = 'ot', _('Other')


class RecurrenceFrequency(models.TextChoices):
    DAILY = 'da', _('Daily')
    WEEKLY = 'we', _('Weekly')
    BIWEEKLY = 'bw', _('Every Two Weeks')
    MONTHLY = 'mo', _('Monthly')
    QUARTERLY = 'qu', _('Quarterly')
    SEMIANNUALLY = 'sa', _('Semi-Annually')
    ANNUALLY = 'an', _('Annually')
