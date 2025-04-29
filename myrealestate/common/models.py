from django.db import models
from djmoney.models.fields import MoneyField

# Create your models here.

class BaseModel(models.Model):
    '''
    Base model for all models. Inherit this model to add created_at, updated_at, created_by, updated_by fields to any model.
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    #updated_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='updated_by')

    class Meta:
        abstract = True



class CurrencyField(MoneyField):
    def __init__(self, *args, **kwargs):
        # Set default max_digits to 22 and decimal_places to 4 if not provided
        kwargs.setdefault('max_digits', 22)
        kwargs.setdefault('decimal_places', 4)
        super().__init__(*args, **kwargs)
        
