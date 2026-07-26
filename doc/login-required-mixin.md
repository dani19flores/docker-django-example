# LoginRequiredMixin

Continuación de [`mixin-instance-redirect-view.md`](mixin-instance-redirect-view.md).

## Qué hace

`LoginRequiredMixin` (de `django.contrib.auth.mixins`) es la versión CBV del
decorador `@login_required` que ya se usaba en `ecommerce/views.py` sobre las
funciones (`product_model_list_view`, etc.).

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class ProductProtectedListView(LoginRequiredMixin, TemplateTitleMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "product_list"
    title = "Mis productos"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
```

- Sobrescribe `dispatch()` — el primer método que corre cualquier CBV al
  recibir un request. Ahí revisa si `request.user.is_authenticated`. Si NO lo
  está, corta el flujo ahí mismo y redirige, **sin que la vista real llegue a
  ejecutarse** (ni `get_queryset`, ni `get_context_data`, nada).
- Redirige a `settings.LOGIN_URL` (en este proyecto: `/admin/login/`, definido
  en `config/settings.py`), agregando `?next=<la-url-original>` — por eso,
  después de iniciar sesión, Django te manda de vuelta exactamente a donde
  intentabas entrar.
- **Orden de la herencia**: `LoginRequiredMixin` va primero (más a la
  izquierda), antes que `TemplateTitleMixin` y que `ListView`. Así su
  `dispatch()` es el que se ejecuta primero en la cadena MRO — si fuera al
  final, la vista ya habría hecho trabajo antes de checar el login.

## `LoginRequiredMixin` no filtra datos por sí solo

El mixin solo garantiza que **haya alguien logueado** — no le importa de
quién son los datos que ve. Para que cada usuario vea solo lo suyo ("Mis
productos"), hacen falta dos cosas más:

1. **Un campo `user` en el modelo** (`products/models.py`):
   ```python
   from django.conf import settings

   class Product(models.Model):
       title = models.CharField(max_length=120)
       slug = models.SlugField(unique=True)
       user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
   ```
   - `settings.AUTH_USER_MODEL` en vez de importar `User` directo — mismo
     patrón que ya se usaba en `ecommerce/models.py` (`ProductModel.user`,
     migración `0005_productmodel_user`, ver [`ecommerce-migrations.md`](ecommerce-migrations.md)).
   - `null=True` + `on_delete=SET_NULL`: si se borra el usuario, el producto
     no se borra, solo queda sin dueño.
   - Se generó y aplicó `products/migrations/0004_product_user.py`.

2. **Sobrescribir `get_queryset()` en la vista**, usando `self.request.user`:
   ```python
   def get_queryset(self):
       return Product.objects.filter(user=self.request.user)
   ```
   `self.request` ya existe en este punto porque `LoginRequiredMixin` corrió
   primero — garantiza que si se llega hasta acá, `self.request.user` es un
   usuario real autenticado, no `AnonymousUser`.

## URL

```python
path('protegido/', views.ProductProtectedListView.as_view(), name="protected-product-list"),
```

## Verificado en el navegador

1. **Sin sesión iniciada**: se visitó `/products/protegido/` → Django
   redirigió a la página de login del admin (`Log in | Django site admin`),
   con `?next=/products/protegido/` en la URL.
2. **Se inició sesión** con el superusuario de prueba (`admin` /
   `testpass123` — contraseña seteada a mano por shell solo para probar en
   este entorno local de Docker, no es una credencial real de producción).
3. **Tras el login**: Django redirigió automáticamente de vuelta a
   `/products/protegido/`.
4. **Después de agregar el campo `user` y el filtro**: se asignó el producto
   `camisa-azul` al usuario `admin` (los otros dos, `pantalon-negro` y
   `tenis-blancos`, se dejaron sin dueño). Al volver a visitar
   `/products/protegido/` logueado como `admin`, la página mostró:
   ```
   Mis productos
   Camisa azul
   ```
   Confirma que el filtro por `user` funciona: los productos sin dueño (o de
   otro usuario) no aparecen, aunque sí existan en la tabla.

## Equivalente en FBV (para comparar)

Ya existía en `ecommerce/views.py`, con el decorador en vez del mixin:

```python
from django.contrib.auth.decorators import login_required

@login_required
def product_model_list_view(request):
    ...
```

Mismo resultado, dos formas de expresarlo según si la vista es función o
clase.
