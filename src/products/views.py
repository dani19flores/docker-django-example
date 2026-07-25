from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, RedirectView

from ecommerce.models import ProductModel


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
