from django.db import models

from ecommerce.models import ProductModel

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField()


# --- modelo proxy ---
#
# ProductProxy usa la MISMA tabla de base de datos que ProductModel (no
# genera una tabla nueva) — solo cambia comportamiento en Python: qué
# manager usa por default y qué métodos tiene disponibles.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            state=ProductModel.PublishStateOptions.PUBLISHED
        )


class ProductProxy(ProductModel):
    objects = PublishedManager()

    class Meta:
        proxy = True

    def pretty_title(self):
        return self.title.title()
