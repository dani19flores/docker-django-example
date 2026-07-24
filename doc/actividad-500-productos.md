# actividad: crear 500 productos y guardarlos en un fixture

Objetivo de la actividad: crear 500 productos de prueba de forma automatizada
(`bulk_create`), exportarlos a un fixture, borrar todo de la base de datos, y
volver a cargarlos desde ese fixture.

## 0. Levantar Docker

```bash
docker compose up -d
docker compose exec web python manage.py migrate
```

## 1. Crear 500 productos con `bulk_create`

```python
from ecommerce.models import ProductModel

products_data = []
for i in range(1, 501):
    new_data = {"title": "Producto {}".format(i), "price": i * 100 + 99.99}
    products_data.append(new_data)

new_objects = []
for product_data in products_data:
    new_objects.append(ProductModel(**product_data))

ProductModel.objects.bulk_create(new_objects, ignore_conflicts=True)
```

```bash
docker compose exec -T web python manage.py shell < bulk_create_500.py
```

## 2. Exportar el fixture

```bash
docker compose exec -T web python manage.py dumpdata ecommerce --indent 4 --format json > ecommerce/fixtures/products/500Products.json
```

## 3. Borrar todo el queryset de productos

```python
from ecommerce.models import ProductModel

ProductModel.objects.all().delete()
```

## 4. Recargar los productos desde el fixture

```bash
docker compose exec web python manage.py loaddata ecommerce/fixtures/products/500Products.json
```
