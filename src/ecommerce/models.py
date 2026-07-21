from django.db import models

from base.models import BasePublishedModel
from .validators import validate_blocked_words

# Create your models here.
class ProductModel(BasePublishedModel):

    title = models.TextField()
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)
    seller = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    product_dimensions = models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        validate_blocked_words(self.title)
        super().save(*args, **kwargs)
