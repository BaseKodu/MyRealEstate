from django.db import models

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

        
