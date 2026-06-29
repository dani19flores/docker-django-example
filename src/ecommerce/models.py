from django.db import models

# Create your models here.
class ProductModel(models.Model):
    title = models.TextField()
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)
    seller = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    product_dimensions = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title