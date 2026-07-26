# ProductModelForm — crear productos

Continuación de [`login-required-mixin.md`](login-required-mixin.md).

## El form

`products/forms.py`:

```python
from django import forms

from .models import Product


class ProductModelForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "slug"]
```

- `forms.ModelForm`: genera automáticamente los campos del formulario (y sus
  validaciones) a partir del modelo — no hay que declarar `title = forms.CharField(...)`
  a mano.
- `Meta.fields`: solo expone `title` y `slug` — el campo `user` (agregado en
  [`login-required-mixin.md`](login-required-mixin.md)) **no** está en la
  lista a propósito: no se le pide al usuario que elija el dueño desde el
  form, se asigna en la vista con el usuario logueado.
- Mismo patrón que `ecommerce/forms.py` (`ProductModelForm` sobre
  `ProductModel`), solo que acá con menos campos.

## Las vistas — dos formas de crear

**FBV** (`product_create_view`):

```python
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
```

- `form.save(commit=False)`: arma el objeto `Product` en memoria pero
  **todavía no lo guarda** en la base de datos — así da tiempo de asignarle
  `instance.user` antes del `.save()` real.
- `@login_required`: mismo decorador que ya usaba `ecommerce/views.py`, para
  que `request.user` exista y no sea `AnonymousUser`.

**CBV** (`ProductCreateView`):

```python
class ProductCreateView(LoginRequiredMixin, CreateView):
    form_class = ProductModelForm
    template_name = "products/product_create.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("products:product-detail", kwargs={"slug": self.object.slug})
```

- `CreateView` ya trae todo el flujo de "mostrar form → validar → guardar →
  redirigir" — solo hay que decirle qué form usar (`form_class`) y qué
  template (`template_name`).
- `form_valid(self, form)`: es el método que `CreateView` llama justo cuando
  el form ya pasó sus validaciones y está por guardarse — equivalente al
  `form.save(commit=False)` + `instance.user = ...` de la FBV, pero
  enganchado al ciclo de vida de la clase en vez de escrito a mano.
- `get_success_url()`: a dónde redirigir después de guardar.
  `self.object` es el objeto recién creado (`CreateView` lo deja guardado ahí
  después de `form_valid`).

## Template

`templates/products/product_create.html`:

```html
<h1>Crear producto</h1>

<form method="POST">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Guardar</button>
</form>
```

El mismo template sirve para las dos vistas (FBV y CBV) — ambas le pasan un
`form` al contexto con el mismo nombre.

## URLs

```python
path('crear/', views.product_create_view, name="product-create"),
path('crear-cbv/', views.product_create_view_cbv, name="product-create-cbv"),
```

## Verificado en el navegador

1. `/products/crear/` (FBV), logueado como `admin`: se llenó `title="Gorra roja"`,
   `slug="gorra-roja"` → redirigió a `/products/list/gorra-roja/` mostrando el
   detalle.
2. `/products/crear-cbv/` (CBV): se llenó `title="Bufanda gris"`,
   `slug="bufanda-gris"` → redirigió igual a `/products/list/bufanda-gris/`.
3. Se visitó `/products/protegido/` ("Mis productos", ver
   [`login-required-mixin.md`](login-required-mixin.md)) y aparecieron los
   dos productos nuevos junto con `camisa-azul` — confirma que
   `instance.user`/`form.instance.user` sí quedó asignado al usuario logueado
   en ambos casos.
