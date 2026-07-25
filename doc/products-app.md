# app `products` — vistas basadas en función vs. en clase

Nueva app creada con `python manage.py startapp products` (dentro del
contenedor, ver [`docker-shell-directo.md`](docker-shell-directo.md)).

## Registro en el proyecto

**`config/settings.py`** — se agregó a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "pages.apps.PagesConfig",
    "products.apps.ProductsConfig",
    "ecommerce.apps.EcommerceConfig",
    "base.apps.BaseConfig",
    ...
]
```

**`config/urls.py`** — se montó bajo el prefijo `/products/`:

```python
path("products/", include("products.urls")), #<--------------- new
```

## `products/urls.py`

```python
urlpatterns = [
    path('about/', TemplateView.as_view(template_name='about.html')),
    path('team/', TemplateView.as_view(template_name='team.html')),
    path('fbv/', views.product_list_view),
    path('cbv/', views.product_list_view_cbv),
]
```

- `/products/about/` y `/products/team/` → páginas estáticas con `TemplateView`.
- `/products/fbv/` y `/products/cbv/` → la misma lista de productos, una
  servida con vista de función y otra con vista de clase, para comparar.

(Se quitó `path('admin/', admin.site.urls)` que estaba duplicado acá — esa
ruta ya vive en `config/urls.py`.)

## Diferencia entre FBV y CBV

Esta era la clase del video: **"Diferencia las vistas basadas en funciones y
las basadas en clases"**. En `products/views.py` quedaron los dos estilos
resolviendo exactamente lo mismo (listar productos), para comparar:

### Vista basada en función (FBV)

```python
def product_list_view(request):
    queryset = ProductModel.objects.all()
    context = {"products": queryset}
    return render(request, "ecommerce/list-view.html", context)
```

- Es una función normal de Python: recibe `request`, hace lo que necesites
  paso a paso, y regresa un `response` (`render`, `HttpResponse`, etc.).
- Todo el flujo (obtener datos, armar el contexto, elegir el template) está
  explícito y en un solo bloque, de arriba hacia abajo.
- Es fácil de leer y de seguir para casos simples, pero si tienes muchas
  vistas que hacen "lo mismo pero con otro modelo" (listar, ver detalle,
  crear, editar, borrar), terminas repitiendo la misma estructura una y otra
  vez.

### Vista basada en clase (CBV)

```python
class ProductListView(ListView):
    queryset = ProductModel.objects.all()
    template_name = "ecommerce/list-view.html"
    context_object_name = "products"

product_list_view_cbv = ProductListView.as_view()
```

- Hereda de una clase genérica de Django (`ListView`) que **ya trae
  implementada** la lógica común de "traer un queryset y renderizarlo en una
  plantilla" — tú solo declaras la configuración (`queryset`, `template_name`,
  `context_object_name`), no escribes el `render()` a mano.
- `.as_view()` convierte la clase en algo que Django pueda usar en
  `urlpatterns` como si fuera una función normal — por eso en las urls se ve
  igual que la FBV.
- Se puede extender con herencia: por ejemplo `ProductDetailView(DetailView)`,
  `ProductCreateView(CreateView)`, reutilizando comportamiento en vez de
  reescribirlo.
- La contrapartida: cuando algo se sale de lo estándar (una regla de negocio
  rara), hay que saber en qué método de la clase padre meter la mano
  (`get_queryset`, `get_context_data`, etc.), lo cual tiene más curva de
  aprendizaje que simplemente escribir una función.

### En resumen

| | FBV | CBV |
|---|---|---|
| Qué es | Una función de Python | Una clase que hereda de una vista genérica |
| Lógica | Explícita, escrita a mano | Heredada, se configura con atributos |
| Mejor para | Casos simples o muy particulares | Patrones repetitivos (listar/crear/editar/borrar) |
| Cómo se usa en `urls.py` | `views.product_list_view` | `views.ProductListView.as_view()` |
