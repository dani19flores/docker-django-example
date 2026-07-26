from django.conf import settings
from django.db import models

from ecommerce.models import ProductModel

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)


# --- modelo proxy vacío ---
#
# DigitalProduct no agrega campos ni métodos nuevos, solo demuestra que un
# proxy puede existir sin cambiar NADA de comportamiento todavía — usa la
# misma tabla y el mismo manager que Product. Sirve como punto de partida
# para, más adelante, personalizarlo (otro manager, otros métodos, otro
# Meta.ordering) sin tocar Product ni su tabla.
class DigitalProduct(Product):
    class Meta:
        proxy = True


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
