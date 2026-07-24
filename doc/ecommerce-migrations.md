# migraciones de `ecommerce`

Historial de migraciones de `ProductModel` y qué agregó cada una.

| Migración | Qué agrega |
|---|---|
| `0001_initial` | Modelo `ProductModel` inicial. |
| `0002_productmodel_color_productmodel_description_and_more` | Campos `color`, `description`, `product_dimensions`. |
| `0003_alter_productmodel_options_and_more` | `ProductModel` pasa a heredar de `BasePublishedModel` (ver [`base-app.md`](base-app.md)): agrega `state`, `timestamp`, `updated`, `published_timestamp`, y actualiza `Meta.options`. |
| `0004_productmodel_slug` | Campo `slug` (ver [`docker-dumpdata.md`](docker-dumpdata.md) para la explicación completa de cómo se genera). |
| `0005_productmodel_user` | Campo `user`, relación con el dueño del producto (ver detalle abajo). |

## `0005_productmodel_user`

Se agregó el campo `user` a `ProductModel`:

```python
from django.conf import settings

User = settings.AUTH_USER_MODEL

class ProductModel(BasePublishedModel):
    ...
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
```

- **`ForeignKey(User, ...)`**: relaciona cada producto con el usuario (`auth.User`) que lo creó/es dueño. Se usa `settings.AUTH_USER_MODEL` en vez de importar `User` directamente, que es la forma recomendada por Django para no acoplarse a un modelo de usuario específico (por si el proyecto llegara a usar un modelo de usuario personalizado).
- **`null=True`**: permite que un producto no tenga usuario asignado (por ejemplo los que se crearon antes de este cambio, o productos creados a granel por script — ver [`shell-bulk-create.md`](shell-bulk-create.md), donde no se pasa `user` al crear los objetos).
- **`on_delete=models.SET_NULL`**: si se borra el usuario dueño, el producto **no se borra** — solo su campo `user` queda en `NULL`. Esto evita perder productos por accidente al eliminar una cuenta.

Para generarla y aplicarla (dentro del contenedor, ver [`docker-dumpdata.md`](docker-dumpdata.md) sobre por qué):

```bash
docker compose exec web python manage.py makemigrations ecommerce
docker compose exec web python manage.py migrate
```
