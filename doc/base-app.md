# app base

Se creó una nueva app `base` para centralizar comportamiento compartido entre modelos.

## `base/models.py`

Se agregó `BasePublishedModel`, un modelo abstracto con el estado de publicación
que antes estaba duplicado en `ProductModel`:

- `state`: choices `PUBLICADO` / `BORRADOR` / `PRIVADO` (default `BORRADOR`)
- `timestamp`, `updated`: fechas automáticas
- `published_timestamp`: se completa solo cuando el estado pasa a `PUBLICADO`
- `state_is_published` (property) e `is_published()` (method)
- `Meta.ordering = ['-updated', '-timestamp']`

## `config/settings.py`

Se agregó `"base.apps.BaseConfig"` a `INSTALLED_APPS`.

## `ecommerce/models.py`

`ProductModel` ahora hereda de `BasePublishedModel` en vez de `models.Model`:

- Se quitó el `PUBLISH_STATE_CHOICES` y el campo `state` que estaban duplicados en `ecommerce`.
- Se quitó el método `is_published()` local (ahora lo hereda de `BasePublishedModel`).

## Migración

`ecommerce/migrations/0003_alter_productmodel_options_and_more.py` — generada con
`python manage.py makemigrations`, agrega los campos nuevos (`published_timestamp`,
`state`, `timestamp`, `updated`) y actualiza `Meta.options` de `ProductModel`.
