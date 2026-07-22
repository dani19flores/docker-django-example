from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
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
    slug = models.SlugField(db_index=True, blank=True, null=True)

    def get_absolute_url(self):
        return f"/products/{self.slug}/"
    
    def save(self, *args, **kwargs):
        validate_blocked_words(self.title)
        super().save(*args, **kwargs)


def slug_pre_save(sender, instance, *args, **kwargs):
    if instance.slug is None or instance.slug == "":
        new_slug = slugify(instance.title)
        MyModel = instance.__class__
        qs =    MyModel.objects.filter(slug=new_slug).exclude(id=instance.id)
        if qs.exists() == 0:
            instance.slug = new_slug
        else:
            instance.slug = f"{new_slug}-{qs.count()}"

pre_save.connect(slug_pre_save, sender=ProductModel)