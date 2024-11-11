from django.db import models

# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    #updated_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='updated_by')

    class Meta:
        abstract = True
