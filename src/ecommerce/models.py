from django.db import models

# Create your models here.
class ProductModel(models.Model):
    title = models.TextField()
    price = models.FloatField()

    def __str__(self):
        return self.title