# creación a granel (shell)

Ejemplo de cómo crear muchos objetos de una sola vez usando `python manage.py shell`.

```bash
python manage.py shell
```

```python
products_data = []
for i in range(1, 100):
    new_data = {"title": "Producto {}".format(i), "price": i * 100 + 99.99}
    products_data.append(new_data)
```

```python
from ecommerce.models import ProductModel

new_objects = []
for product_data in products_data:
    print(product_data)
    new_objects.append(ProductModel(**product_data))
```

```python
ProductModel.objects.bulk_create(new_objects, ignore_conflicts=True)
```
