# levantar contenedores y exportar datos (dumpdata)

## 1. Levantar los servicios de Docker

Los comandos de `manage.py` que tocan la base de datos necesitan correr **dentro**
del contenedor `web`, porque el host `postgres` solo se resuelve dentro de la red
de Docker (el `postgres` de `compose.yaml` no publica puerto al host).

```bash
docker compose up -d
```

## 2. Migración faltante del campo `slug`

Al correr `dumpdata` la primera vez salió este error:

```
CommandError: Unable to serialize database: column ecommerce_productmodel.slug does not exist
```

El campo `slug` ya existía en `ecommerce/models.py`, pero nunca se había generado
su archivo de migración. Se generó y se aplicó dentro del contenedor:

```bash
docker compose exec web python manage.py makemigrations ecommerce
docker compose exec web python manage.py migrate
```

Esto creó `ecommerce/migrations/0004_productmodel_slug.py` y la aplicó a la base
de datos de Postgres del contenedor.

Para confirmar que quedó aplicada:

```bash
docker compose exec web python manage.py showmigrations ecommerce
```

## 3. Exportar datos de `ecommerce` (dumpdata)

```bash
docker compose exec web python manage.py dumpdata ecommerce --indent 4 --format json
```

Y guardándolo como fixture dentro de la app:

```bash
docker compose exec web python manage.py dumpdata ecommerce --indent 4 --format json > ecommerce/fixtures/ProductModel.json
```

`dumpdata` serializa el contenido actual de la base de datos (todas las filas de
los modelos de la app `ecommerce`) a JSON. Guardarlo en `fixtures/` permite luego
recargar esos mismos datos en otra base de datos (por ejemplo en un ambiente nuevo)
con `python manage.py loaddata ProductModel.json`.

## ¿Qué es el `slug`?

Un **slug** es una versión del texto (normalmente el título) convertida a un
formato apto para URLs: en minúsculas, sin espacios ni acentos ni caracteres
especiales, con guiones en vez de espacios. Por ejemplo:

```
"Laptop Gamer Pro" → "laptop-gamer-pro"
```

En `ecommerce/models.py`, `ProductModel` usa el slug para armar la URL del
producto:

```python
def get_absolute_url(self):
    return f"/products/{self.slug}/"
```

El slug se genera automáticamente antes de guardar el objeto, mediante una señal
`pre_save` (`slug_pre_save`) conectada al modelo:

```python
def slug_pre_save(sender, instance, *args, **kwargs):
    if instance.slug is None or instance.slug == "":
        new_slug = slugify(instance.title)
        qs = ProductModel.objects.filter(slug=new_slug).exclude(id=instance.id)
        if not qs.exists():
            instance.slug = new_slug
        else:
            instance.slug = f"{new_slug}-{qs.count()}"

pre_save.connect(slug_pre_save, sender=ProductModel)
```

- Si el producto no tiene slug todavía, lo genera con `slugify(title)`.
- Si ya existe otro producto con ese mismo slug, le agrega un sufijo numérico
  (`-1`, `-2`, etc.) para que no se repita, ya que el slug se usa para identificar
  el producto en la URL y por eso debe ser único.
- Como el slug se asigna en `pre_save` (justo antes de guardar) y no al momento de
  crear el objeto en memoria, los productos creados con `bulk_create` (ver
  [`shell-bulk-create.md`](shell-bulk-create.md)) no disparan esa señal — por eso
  en el `dumpdata` de arriba aparecen productos con `"slug": null`.
