# documentación de comandos 
## migración
python manage.py makemigration
python manage.py migrate

## Borrar migraciones
python manage.py squashmigrations <APP_LABEL> <MIGRATION_NUMBER>
python manage.py squashmigrations ecommers 004
python manage.py migrate