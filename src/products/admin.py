from django.contrib import admin

# Register your models here.
from .models import Product, ProductProxy

admin.site.register(Product)
admin.site.register(ProductProxy)

