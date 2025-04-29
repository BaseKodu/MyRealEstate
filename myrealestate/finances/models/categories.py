from django.db import models
from myrealestate.common.models import BaseModel
from .enums import CategoryType

class FinancialCategory(BaseModel):
    """Categories for financial transactions (both income and expenses)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category_type = models.CharField(max_length=1, choices=CategoryType.choices)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name="financial_categories")
    is_default = models.BooleanField(default=False)
    is_tax_deductible = models.BooleanField(default=False, help_text="Indicates if this expense category is tax deductible")
    
    class Meta:
        unique_together = ('name', 'company', 'category_type')
        ordering = ['name']
        verbose_name_plural = "Financial categories"
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"
