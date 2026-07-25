# Mixin propio + RedirectView basada en la instancia del modelo

Continuación de [`context-data-proxy-model.md`](context-data-proxy-model.md).

## 1. Un mixin genérico para heredar en vistas

`products/mixins.py`:

```python
class TemplateTitleMixin(object):
    title = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = self.get_title()
        return context

    def get_title(self):
        return self.title
```

- Es una clase normal de Python, **sin heredar de nada de Django** — no es
  una vista por sí sola, solo aporta comportamiento para que otra vista lo
  combine.
- Cualquier CBV que la herede (junto con una vista real, como `ListView` o
  `DetailView`) obtiene automáticamente un `title` en el contexto, sin tener
  que repetir el mismo `get_context_data` en cada vista.
- `super().get_context_data(*args, **kwargs)`: sigue el mismo patrón que en
  [`context-data-proxy-model.md`](context-data-proxy-model.md) — primero se
  arma el contexto normal de la vista, y luego se le agrega `title` encima.

Se aplicó a las vistas "auto" (las que usan resolución automática de
templates, ver [`redirect-list-detail-views.md`](redirect-list-detail-views.md))
y a la nueva `DigitalProductListView`:

```python
class ProductAutoListView(TemplateTitleMixin, ListView):
    model = Product
    title = "Listado de productos"


class ProductAutoDetailView(TemplateTitleMixin, DetailView):
    model = Product
    slug_field = "slug"
    slug_url_kwarg = "slug"
    title = "Detalle de producto"


class DigitalProductListView(TemplateTitleMixin, ListView):
    model = DigitalProduct
    template_name = "products/product_list.html"
    context_object_name = "product_list"  # el template espera este nombre
    title = "Listado de productos digitales"
```

- **Orden de la herencia importa**: el mixin va **antes** que
  `ListView`/`DetailView`. Python resuelve `get_context_data` de izquierda a
  derecha (MRO), así que el mixin se ejecuta primero y su `super()` termina
  llegando al `get_context_data` real de `ListView`/`DetailView`. Si el orden
  fuera al revés, el mixin nunca se llamaría.
- En `DigitalProductListView` hubo que fijar `context_object_name` a mano:
  como el modelo es `DigitalProduct` (no `Product`), el nombre automático que
  arma `ListView` sería `digitalproduct_list`, y el template
  `product_list.html` espera `product_list` en el `{% for %}`.

(Nombre original de este mixin durante la exploración: `TemplateResponseMixin`
— se renombró a `TemplateTitleMixin` para que coincida con el de la clase, y
de paso porque `TemplateResponseMixin` ya es el nombre de un mixin real de
Django, `django.views.generic.base.TemplateResponseMixin` — mismo nombre,
clase distinta, mejor evitar la confusión.)

## 2. RedirectView basada en la instancia del modelo — dos técnicas

**Técnica A — a mano, leyendo `self.kwargs`** (la de la clase):

```python
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
```

- `ProductIDRedirectView`: recibe un `pk` en la URL, busca el objeto con
  `get_object_or_404` y redirige a la URL "bonita" (con slug).
- `ProductRedirectView`: ni siquiera necesita ir a la base de datos — solo
  reacomoda el slug que ya venía en la URL hacia otra ruta. Útil para
  redirigir de una URL vieja/corta a la canónica sin gastar una consulta.
- `self.kwargs` es el diccionario con los parámetros que capturó `path()` de
  la URL (`pk`, `slug`, lo que sea que se haya definido con `<...>` en la
  ruta).

**Técnica B — con `SingleObjectMixin`** (la que se había armado antes):

```python
from django.views.generic.detail import SingleObjectMixin

class ProductInstanceRedirectView(SingleObjectMixin, RedirectView):
    queryset = ProductModel.objects.all()

    def get_redirect_url(self, *args, **kwargs):
        obj = self.get_object()
        return obj.get_absolute_url()
```

- `SingleObjectMixin` es el mixin GENÉRICO que trae Django para "buscar un
  objeto" — lo usan por dentro `DetailView`, `UpdateView`, `DeleteView`.
  Aporta el método `get_object()`, que ya sabe buscar por `pk` (o por `slug`
  si se configuran `slug_field`/`slug_url_kwarg`) usando `queryset` +
  `self.kwargs`, sin que tengas que leerlo tú mismo.
- Es menos código, pero exige entender de antemano qué hace `SingleObjectMixin`
  por dentro. La Técnica A es más explícita — mejor para aprender qué pasa,
  antes de "delegarlo" a un mixin de Django.
- Este usa `ProductModel` (de `ecommerce`, con datos reales y
  `get_absolute_url()` propio) en vez de `Product`.

## 3. Modelo proxy `DigitalProduct`

```python
# products/models.py
class DigitalProduct(Product):
    class Meta:
        proxy = True
```

- Proxy **vacío**: no agrega campos ni métodos, ni cambia el manager — usa
  exactamente la misma tabla y los mismos datos que `Product` (a diferencia
  de `ProductProxy`, que sí filtraba por `state="PUBLICADO"`, ver
  [`context-data-proxy-model.md`](context-data-proxy-model.md)).
- Sirve para demostrar que un `ListView`/`DetailView` puede apuntar a un
  proxy sin que cambie nada más: `DigitalProductListView` lista los mismos
  3 productos que `ProductAutoListView`, solo que a través de otro modelo
  (otro "punto de entrada" a la misma tabla).
- Sí generó una migración (`0003_digitalproduct_alter_product_slug`) — igual
  que con `ProductProxy`, es solo para que Django registre el modelo
  (permisos, `content_type`), no crea tabla nueva.

## 4. Configurar el slug como único

Se aplicó en **dos modelos** distintos:

```python
# ecommerce/models.py — ProductModel
slug = models.SlugField(db_index=True, blank=True, null=True, unique=True)
```

```python
# products/models.py — Product
slug = models.SlugField(unique=True)
```

```bash
docker compose exec web python manage.py makemigrations ecommerce products
docker compose exec web python manage.py migrate
```

- Antes de aplicar el cambio en `ecommerce` se verificó que no hubiera slugs
  duplicados ni nulos entre los 506 productos existentes — si hubiera habido
  duplicados, la migración habría fallado al crear el índice único.
- `unique=True` + `null=True` es válido: en Postgres, múltiples valores
  `NULL` no violan una restricción `UNIQUE` (solo los valores no-nulos deben
  ser distintos entre sí).
- Por qué importa para las URLs: si dos productos tuvieran el mismo slug, las
  vistas que buscan por `slug=...` (`ProductDetailView`, `ProductAutoDetailView`,
  `ProductIDRedirectView`) podrían encontrar el objeto equivocado, o Django
  lanzaría `MultipleObjectsReturned` en vez de servir el producto correcto.

## 5. URLs completas de esta sección

```python
path('digital-products/', views.DigitalProductListView.as_view(), name="digital-product-list"),

path('id/<int:pk>/', views.ProductIDRedirectView.as_view(), name="product-id-redirect"),
path('slug-redirect/<slug:slug>/', views.ProductRedirectView.as_view(), name="product-slug-redirect"),

# estas dos van al final: <slug:slug>/ es un "catch-all" que matchea
# cualquier texto simple, así que tiene que evaluarse después de todas
# las rutas literales de arriba (si no, se las "come" a ellas).
path('<int:pk>/', views.ProductInstanceRedirectView.as_view(), name="instance-redirect"),
path('<slug:slug>/', views.ProductDetailView.as_view(), name="detail"),
```

Nota sobre el proyecto de referencia (el del video): ahí `products` **es** el
proyecto completo — su `urls.py` es el urlconf raíz (incluye hasta
`admin.site.urls` ahí mismo), así que sus rutas son directas
(`/products/<slug>/`, `/p/<slug>/`). En este proyecto, `products` es una app
más, montada bajo `/products/` desde `config/urls.py` — por eso las rutas acá
quedan anidadas (`/products/list/<slug>/`, `/products/id/<pk>/`, etc.) en vez
de replicar exactamente esas mismas rutas cortas.

## 6. Verificado en el navegador

- `/products/id/2/` → redirige a `/products/list/pantalon-negro/`.
- `/products/slug-redirect/tenis-blancos/` → redirige a
  `/products/list/tenis-blancos/`.
- `/products/9/` → redirige a `/products/producto-1/` (técnica B, con
  `ProductModel`/`ecommerce`).
- `/products/digital-products/` → título "Listado de productos digitales"
  (del mixin) + los mismos 3 productos que `/products/list/`.
- Se intentó crear un producto nuevo con `slug="producto-1"` (ya existente) a
  propósito, por shell:
  ```
  IntegrityError: duplicate key value violates unique constraint
  "ecommerce_productmodel_slug_71830311_uniq"
  ```
  Confirma que la restricción `unique=True` sí se aplica a nivel de base de
  datos, no solo en formularios de Django.
