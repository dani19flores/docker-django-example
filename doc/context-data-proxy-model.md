# get_context_data() y modelos proxy

Continuación de [`redirect-list-detail-views.md`](redirect-list-detail-views.md).
Ejemplo completo: `products/publicados/` — una lista de productos **publicados**,
usando un modelo proxy y una vista que agrega datos extra al contexto.

## 1. Sobrescribir `get_context_data`

`get_context_data()` es el método que las vistas genéricas de Django
(`ListView`, `DetailView`, etc.) usan internamente para armar el diccionario
que se le pasa al template. Sobrescribirlo permite **agregar información
extra** sin reescribir toda la vista desde cero.

```python
class ProductProxyListView(ListView):
    model = ProductProxy
    template_name = "products/product-proxy-list.html"
    context_object_name = "products"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["page_title"] = "Productos publicados"
        context["total_published"] = self.get_queryset().count()
        return context
```

- **Siempre se llama a `super().get_context_data(...)` primero** — ahí es
  donde Django ya mete el queryset (`products`, por `context_object_name`),
  la paginación, etc. Si no lo llamas, pierdes todo eso.
- Después, agregas lo que necesites al diccionario `context` como si fuera
  cualquier `dict` de Python (`page_title`, `total_published`).
- En el template, esas claves están disponibles igual que cualquier variable
  de contexto normal:

```html
<h1>{{ page_title }}</h1>
<p>Total publicados: {{ total_published }}</p>
```

Es la misma idea que ya se usaba en las FBV de este proyecto
(`context = {"products": queryset}` en [`product_list_view`](../src/products/views.py))
— `get_context_data` es la versión de "CBV" de armar ese mismo diccionario,
pero partiendo de lo que Django ya te da gratis.

## 2. Modelo estándar vs. modelo proxy

Un **modelo estándar** (como `ProductModel` o `Product`) crea su propia tabla
en la base de datos cuando corres `migrate`.

Un **modelo proxy** (`class Meta: proxy = True`) **no crea tabla nueva** — usa
exactamente la misma tabla del modelo del que hereda. Solo cambia
comportamiento en el lado de Python: qué manager usa por default, qué
métodos tiene, el ordering, etc.

```python
# products/models.py
from ecommerce.models import ProductModel


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
```

- **`ProductProxy(ProductModel)`**: hereda de un modelo "real" que vive en
  **otra app** (`ecommerce`) — los proxys no tienen que estar en la misma app
  que su modelo padre.
- **`objects = PublishedManager()`**: reemplaza el manager por default.
  Cualquier `ProductProxy.objects...` ya viene filtrado a
  `state="PU"` (publicado) — no hace falta repetir el `.filter(...)` en cada
  vista que use este modelo.
- **`pretty_title()`**: un método nuevo que **no existe** en `ProductModel`
  — los objetos `ProductProxy` lo tienen disponible, pero si tomas el mismo
  registro desde `ProductModel.objects...` (el modelo original), no lo va a
  tener.
- **`Meta.proxy = True`**: esta línea es la que le dice a Django "no crees
  tabla, usa la de `ProductModel`".

Al correr `makemigrations` para un proxy, Django sí genera un archivo de
migración (`products/migrations/0002_productproxy.py`), pero es solo para
registrar el modelo (permisos, `content_type`, etc.) — no ejecuta ningún
`CREATE TABLE` en la base de datos:

```bash
docker compose exec web python manage.py makemigrations products
docker compose exec web python manage.py migrate products
```

## 3. La vista completa

```python
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
```

```python
# products/urls.py
path('publicados/', views.product_proxy_list_view, name="published-products"),
```

```html
<!-- templates/products/product-proxy-list.html -->
<h1>{{ page_title }}</h1>
<p>Total publicados: {{ total_published }}</p>

<ul>
{% for product in products %}
    <li>{{ product.pretty_title }} — ${{ product.price }}</li>
{% empty %}
    <li>No hay productos publicados todavía.</li>
{% endfor %}
</ul>
```

## 4. Evaluación / qué se probó

Para poder ver el filtro funcionando, se marcaron 3 productos existentes
(`laptop`, `Mouse`, `escritorio elevable`) con `state="PU"` (publicado):

```python
from ecommerce.models import ProductModel

qs = ProductModel.objects.filter(title__in=["laptop", "Mouse", "escritorio elevable"])
qs.update(state=ProductModel.PublishStateOptions.PUBLISHED)
```

Resultado verificado en `http://localhost:8000/products/publicados/`:

```
Productos publicados
Total publicados: 3

Laptop — $2000.0
Escritorio Elevable — $6500.0
Mouse — $1200.0
```

- El **título** y el **conteo** vienen de `get_context_data` (no existirían
  si solo se usara la lista de `ListView` por default).
- Solo aparecen **3 de los 500+ productos** que hay en la base — el manager
  del modelo proxy filtró todo el resto sin que la vista tuviera que hacerlo.
- `pretty_title()` capitaliza cada palabra (`"escritorio elevable"` →
  `"Escritorio Elevable"`) — confirma que se está usando `ProductProxy` (que
  tiene ese método) y no `ProductModel` directo (que no lo tiene).
