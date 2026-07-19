from django.db import models

from .validators import validate_blocked_words

# [(VALOR_EN_DB, VALOR_PARA_USUARIO)]
PUBLISH_STATE_CHOICES = [
    ('BR', 'BORRADOR'),
    ('PU', 'PUBLICADO'),
    ('PR','PRIVADO')
]

# Create your models here.
class ProductModel(models.Model):
    state = models.CharField(max_length=2, choices=PUBLISH_STATE_CHOICES)
    title = models.TextField()
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)
    seller = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    product_dimensions = models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        validate_blocked_words(self.title)
        super().save(*args, **kwargs)

    def is_published(self):
        return self.state == 'PU'
    
