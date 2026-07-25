from django.views.generic import ListView
from django.shortcuts import render

from ecommerce.models import ProductModel


# vista basada en función (FBV): una función normal de Python que recibe
# el request y devuelve un response.
def product_list_view(request):
    queryset = ProductModel.objects.all()
    context = {"products": queryset}
    return render(request, "ecommerce/list-view.html", context)


# vista basada en clase (CBV): hace lo mismo que la de arriba, pero
# usando la clase genérica ListView de Django, que ya trae resuelta
# la lógica de "traer un queryset y renderizarlo en una plantilla".
class ProductListView(ListView):
    queryset = ProductModel.objects.all()
    template_name = "ecommerce/list-view.html"
    context_object_name = "products"


product_list_view_cbv = ProductListView.as_view()
