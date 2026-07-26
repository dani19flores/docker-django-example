from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, RedirectView
from django.views.generic.detail import SingleObjectMixin

from ecommerce.models import ProductModel
from .forms import ProductModelForm
from .mixins import TemplateTitleMixin
from .models import DigitalProduct, Product, ProductProxy


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


class ProductAutoListView(TemplateTitleMixin, ListView):
    model = Product
    title = "Listado de productos"


class ProductAutoDetailView(TemplateTitleMixin, DetailView):
    model = Product
    slug_field = "slug"
    slug_url_kwarg = "slug"
    title = "Detalle de producto"


# DigitalProduct es un proxy vacío de Product (misma tabla, sin cambios de
# comportamiento todavía). Esta vista demuestra que un ListView puede apuntar
# a un modelo proxy exactamente igual que a su modelo original — por ahora
# lista los mismos registros que ProductAutoListView.
class DigitalProductListView(TemplateTitleMixin, ListView):
    model = DigitalProduct
    template_name = "products/product_list.html"
    context_object_name = "product_list"  # el template espera este nombre
    title = "Listado de productos digitales"


# --- LoginRequiredMixin: protege una vista completa detrás de login ---
#
# Cualquier CBV que herede de LoginRequiredMixin ejecuta su propio dispatch()
# ANTES que el de la vista real: revisa si request.user está autenticado, y
# si no lo está, redirige a LOGIN_URL (configurado en settings.py como
# "/admin/login/") con "?next=<la-url-que-pediste>" para volver acá después
# de iniciar sesión. La vista ni siquiera llega a ejecutar get_queryset().
class ProductProtectedListView(LoginRequiredMixin, TemplateTitleMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "product_list"
    title = "Mis productos"

    # Solo los productos del usuario logueado — self.request.user ya existe
    # acá porque LoginRequiredMixin garantiza que dispatch() no llega hasta
    # este punto si no hay sesión iniciada.
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)


# --- ProductModelForm: crear un producto ---

# FBV
@login_required
def product_create_view(request):
    form = ProductModelForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        return HttpResponseRedirect(
            reverse("products:product-detail", kwargs={"slug": instance.slug})
        )
    context = {"form": form}
    return render(request, "products/product_create.html", context)


# CBV
class ProductCreateView(LoginRequiredMixin, CreateView):
    form_class = ProductModelForm
    template_name = "products/product_create.html"

    # form_valid() es lo que CreateView llama cuando el form pasó sus
    # validaciones y ya está por guardar — acá se aprovecha para asignar el
    # dueño antes de guardar, igual que hace la FBV con instance.user.
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("products:product-detail", kwargs={"slug": self.object.slug})


product_create_view_cbv = ProductCreateView.as_view()


# --- RedirectView basada en la instancia del modelo ---
#
# No usan ningún mixin genérico de Django para buscar el objeto — leen el
# parámetro directo de self.kwargs (lo que capturó la URL) y hacen el
# get_object_or_404 a mano. Es más manual que SingleObjectMixin, pero más
# fácil de leer para quien recién está aprendiendo qué hace un RedirectView.
class ProductIDRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url_params = self.kwargs
        pk = url_params.get("pk")
        obj = get_object_or_404(Product, pk=pk)
        slug = obj.slug
        return f"/products/list/{slug}/"


class ProductRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url_params = self.kwargs
        slug = url_params.get("slug")
        return f"/products/list/{slug}/"


# La misma idea de arriba (ProductIDRedirectView), pero usando
# SingleObjectMixin — el mixin GENÉRICO que trae Django para "buscar un
# objeto" (lo usan por dentro DetailView/UpdateView/DeleteView). En vez de
# leer self.kwargs a mano, self.get_object() ya sabe hacerlo por ti a partir
# de `queryset` + el parámetro de la URL.
class ProductInstanceRedirectView(SingleObjectMixin, RedirectView):
    queryset = ProductModel.objects.all()

    def get_redirect_url(self, *args, **kwargs):
        obj = self.get_object()
        return obj.get_absolute_url()


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
