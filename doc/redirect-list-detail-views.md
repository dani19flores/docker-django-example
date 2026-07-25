# explorando RedirectView, ListView y DetailView

Continuación de [`products-app.md`](products-app.md) (FBV vs CBV). Acá se
comparan tres vistas genéricas de Django (`django.views.generic`) contra su
equivalente escrito a mano como función, todas en `products/views.py` /
`products/urls.py`.

## RedirectView — redirige a otra URL

**FBV** (`about_us_redirect_view`):

```python
def about_us_redirect_view(request):
    return HttpResponseRedirect("/products/about/")
```

**CBV** (`AboutRedirectView`):

```python
class AboutRedirectView(RedirectView):
    url = "/products/about/"
```

- La FBV arma el redirect a mano con `HttpResponseRedirect`.
- La CBV solo declara el atributo `url` — `RedirectView` internamente hace el
  mismo `HttpResponseRedirect` por ti. También se puede usar sin crear una
  clase aparte, directo en `urls.py`:
  ```python
  path('about-us/', RedirectView.as_view(url='/products/about/')),
  ```
- Rutas de prueba: `/products/about-us/`, `/products/about-us-fbv/`,
  `/products/about-us-cbv/` — las tres terminan en `/products/about/`.

## ListView — lista un queryset

Ya se había armado en la actividad anterior (ver
[`products-app.md`](products-app.md)):

```python
class ProductListView(ListView):
    queryset = ProductModel.objects.all()
    template_name = "ecommerce/list-view.html"
    context_object_name = "products"
```

- `context_object_name`: el nombre con el que el queryset llega al template
  (`{{ products }}`). Sin esto, `ListView` usa por default
  `object_list`/`productmodel_list`, menos claro.
- Rutas: `/products/fbv/` (función) y `/products/cbv/` (clase).

## DetailView — muestra un solo objeto

**FBV** (`product_detail_view`):

```python
def product_detail_view(request, slug):
    instance = get_object_or_404(ProductModel, slug=slug)
    context = {"product": instance}
    return render(request, "ecommerce/detail-view.html", context)
```

**CBV** (`ProductDetailView`):

```python
class ProductDetailView(DetailView):
    queryset = ProductModel.objects.all()
    template_name = "ecommerce/detail-view.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"
```

- `get_object_or_404` en la FBV hace lo mismo que `DetailView` hace solo
  internamente: busca un objeto y, si no existe, responde `404` en vez de
  reventar con una excepción sin manejar.
- `slug_field`: el campo del modelo donde está el slug (`ProductModel.slug`).
- `slug_url_kwarg`: el nombre del parámetro capturado en la URL que trae ese
  valor — tiene que coincidir con lo que se declara en `urls.py`
  (`<slug:slug>`).
- `context_object_name = "product"`: para que el template
  `ecommerce/detail-view.html` (que espera `{{ product.title }}`,
  `{{ product.price }}`, etc.) reciba el objeto con ese nombre. Por default
  `DetailView` lo hubiera llamado `productmodel` (el nombre del modelo en
  minúscula), y el template no lo hubiera encontrado.
- Rutas: `/products/fbv/<slug>/` y `/products/cbv/<slug>/` — por ejemplo
  `/products/fbv/producto-1/` y `/products/cbv/producto-1/`.

## `products/urls.py` completo

```python
urlpatterns = [
    path('about/', TemplateView.as_view(template_name='about.html')),
    path('about-us/', RedirectView.as_view(url='/products/about/')),  # CBV inline
    path('about-us-fbv/', views.about_us_redirect_view),               # FBV
    path('about-us-cbv/', views.AboutRedirectView.as_view()),          # CBV como clase aparte
    path('team/', TemplateView.as_view(template_name='team.html')),
    path('fbv/', views.product_list_view),
    path('cbv/', views.product_list_view_cbv),
    path('fbv/<slug:slug>/', views.product_detail_view),
    path('cbv/<slug:slug>/', views.product_detail_view_cbv),
]
```

## Resumen

| Vista genérica | Qué reemplaza | Atributos clave |
|---|---|---|
| `RedirectView` | Un `return HttpResponseRedirect(...)` | `url` |
| `ListView` | Un `render` con un queryset completo | `queryset`/`model`, `template_name`, `context_object_name` |
| `DetailView` | Un `get_object_or_404` + `render` | `queryset`/`model`, `slug_field`, `slug_url_kwarg`, `context_object_name` |

## Nota sobre `products/models.py`

Se agregó un modelo `Product` propio (`title`, `slug`) en `products/models.py`,
pero **todavía no tiene migración generada** y no se usó en ninguna de estas
vistas — los ejemplos de arriba usan `ProductModel` de `ecommerce`, que ya
tenía datos reales (los 500 productos de la actividad anterior) para poder
probar las vistas en el navegador. Si más adelante se quiere migrar estas
vistas para que usen el modelo `Product` propio de `products`, hay que correr
`makemigrations`/`migrate` primero.

Verificado en el navegador: las tres redirecciones, `/products/fbv/producto-1/`
y `/products/cbv/producto-1/` funcionan y muestran el mismo producto.
