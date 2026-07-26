# UpdateView y DeleteView

Continuación de [`product-model-form.md`](product-model-form.md).

## Las vistas

```python
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProductModelForm
    template_name = "products/product_create.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("products:product-detail", kwargs={"slug": self.object.slug})


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "products/FormsDelete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("products:protected-product-list")
```

- `UpdateView` reutiliza `ProductModelForm` (el mismo de
  [`product-model-form.md`](product-model-form.md)) — precarga el form con
  los datos del objeto encontrado y, al guardar, actualiza ese mismo registro
  en vez de crear uno nuevo.
- `DeleteView` no usa ningún form de campos — solo necesita confirmar (un
  `POST` sin campos) para borrar el objeto.
- Ambas comparten `slug_field`/`slug_url_kwarg` — así saben buscar el objeto
  por el `slug` que viene en la URL.

## `get_queryset()` — por qué es la parte que importa de seguridad

`UpdateView` y `DeleteView` (como `DetailView`) resuelven el objeto con
`self.get_object()`, que busca **dentro de `self.get_queryset()`** — no
directo en `Product.objects.all()`.

```python
def get_queryset(self):
    return Product.objects.filter(user=self.request.user)
```

Sin este filtro, cualquier usuario logueado podría editar o borrar el
producto de **otro usuario** con solo escribir su slug en la URL — ya que
`LoginRequiredMixin` únicamente verifica que haya sesión, no de quién es el
objeto (mismo punto que en
[`login-required-mixin.md`](login-required-mixin.md)).

Con el filtro puesto, si el producto no pertenece al usuario logueado, no
aparece en `get_queryset()` → `get_object()` no lo encuentra →
Django responde **404**, en vez de dejar pasar la edición/borrado.

## `get_success_url()` — a dónde ir después

- En `ProductUpdateView`: de vuelta al detalle del producto
  (`self.object.slug` sigue existiendo, porque solo se editó, no se borró).
- En `ProductDeleteView`: a la lista de "Mis productos"
  (`protected-product-list`, ver [`login-required-mixin.md`](login-required-mixin.md))
  — después de borrar, `self.object.slug` ya no tiene sentido como destino
  porque ese producto ya no existe.

## Template `FormsDelete.html`

```html
<h1>Eliminar producto</h1>

<p>¿Seguro que quieres eliminar "{{ object.title }}"? Esta acción no se puede deshacer.</p>

<form method="POST">
    {% csrf_token %}
    <button type="submit">Sí, eliminar</button>
    <a href="{% url 'products:product-detail' slug=object.slug %}">Cancelar</a>
</form>
```

- `DeleteView` en un `GET` solo **muestra** esta página de confirmación — no
  borra nada todavía. El borrado real ocurre cuando el `<form>` se envía por
  `POST`.
- `{{ object }}` es el nombre de contexto que usan por default
  `DetailView`/`UpdateView`/`DeleteView` cuando no se define
  `context_object_name` — por eso el template usa `object.title` en vez de
  `product.title`.

## Links de editar/eliminar (solo para el dueño)

En `templates/products/product_detail.html`:

```html
{% if request.user.is_authenticated and product.user_id == request.user.id %}
    <p>
        <a href="{% url 'products:product-update' slug=product.slug %}">Editar</a> |
        <a href="{% url 'products:product-delete' slug=product.slug %}">Eliminar</a>
    </p>
{% endif %}
```

Esto es solo para **no mostrar el link** si no eres el dueño — es una mejora
de UX, no de seguridad. La seguridad real ya la da `get_queryset()` en la
vista: aunque alguien escriba la URL directamente sin ver el link, igual le
va a dar 404 si el producto no es suyo.

## URLs

```python
path('editar/<slug:slug>/', views.ProductUpdateView.as_view(), name="product-update"),
path('eliminar/<slug:slug>/', views.ProductDeleteView.as_view(), name="product-delete"),
```

## Verificado en el navegador

1. `/products/list/gorra-roja/` (dueño: `admin`, logueado como `admin`) →
   aparecen los links "Editar | Eliminar".
2. `/products/editar/gorra-roja/` → se cambió el título a
   "Gorra roja edición" → redirigió al detalle mostrando el nuevo título.
3. `/products/eliminar/bufanda-gris/` → mostró la página de confirmación →
   se envió el form → redirigió a `/products/protegido/` ("Mis productos"),
   y "Bufanda gris" ya no aparece en la lista.
4. `/products/editar/pantalon-negro/` (producto sin dueño, `user=None`,
   logueado como `admin`) → **404 Page not found** — confirma que
   `get_queryset()` sí está bloqueando el acceso a productos ajenos.
