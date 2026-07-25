from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, RedirectView

from ecommerce.models import ProductModel

from .models import Product, ProductProxy


# --- RedirectView: manda al usuario a otra URL ---

# FBV
def about_us_redirect_view(request):
    return HttpResponseRedirect("/products/about/")


# CBV
class AboutRedirectView(RedirectView):
    url = "/products/about/"


# --- ListView: lista todos los productos ---

# FBV
def product_list_view(request):
    queryset = ProductModel.objects.all()
    context = {"products": queryset}
    return render(request, "ecommerce/list-view.html", context)


# CBV
class ProductListView(ListView):
    queryset = ProductModel.objects.all()
    template_name = "ecommerce/list-view.html"
    context_object_name = "products"


product_list_view_cbv = ProductListView.as_view()


# --- DetailView: muestra un solo producto, buscado por su slug ---

# FBV
def product_detail_view(request, slug):
    instance = get_object_or_404(ProductModel, slug=slug)
    context = {"product": instance}
    return render(request, "ecommerce/detail-view.html", context)


# CBV
class ProductDetailView(DetailView):
    queryset = ProductModel.objects.all()
    template_name = "ecommerce/detail-view.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"


product_detail_view_cbv = ProductDetailView.as_view()


# --- ListView/DetailView sin `template_name`: resolución automática ---
#
# Si no defines `template_name`, Django busca el template por convención:
#   ListView   -> "<app_label>/<model_name>_list.html"
#   DetailView -> "<app_label>/<model_name>_detail.html"
#
# Como el modelo es `Product` de la app `products`, busca
# "products/product_list.html" y "products/product_detail.html" —
# justo los archivos que ya existen en templates/products/.


class ProductAutoListView(ListView):
    model = Product


class ProductAutoDetailView(DetailView):
    model = Product
    slug_field = "slug"
    slug_url_kwarg = "slug"


# --- Modelo proxy + get_context_data ---
#
# ProductProxy (definido en products/models.py) es un modelo PROXY de
# ProductModel: comparte la misma tabla, pero su manager (`objects`) ya
# viene filtrado para traer solo los productos con state="PUBLICADO".
#
# get_context_data() es el método que ListView/DetailView usan para armar
# el diccionario de contexto que llega al template. Sobrescribirlo permite
# agregar datos extra sin tener que escribir toda la vista desde cero.
class ProductProxyListView(ListView):
    model = ProductProxy
    template_name = "products/product-proxy-list.html"
    context_object_name = "products"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["page_title"] = "Productos publicados"
        context["total_published"] = self.get_queryset().count()
        return context


product_proxy_list_view = ProductProxyListView.as_view()
