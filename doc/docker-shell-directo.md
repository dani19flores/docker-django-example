# entrar directo al contenedor (sin repetir docker compose exec)

En vez de anteponer `docker compose exec web python manage.py ...` en cada
comando, puedes entrar una sola vez a una terminal (bash) **dentro** del
contenedor `web` y desde ahí correr todo directo, como si estuvieras en Linux.

## 1. Ver los contenedores corriendo

```bash
docker ps
```

Confirma que el contenedor esté arriba y te da su nombre exacto (por ejemplo
`hellodjango-web-1`). Si no aparece nada, primero hay que levantar los
servicios con `docker compose up -d`.

## 2. Entrar al contenedor con una terminal interactiva

```bash
docker exec -it hellodjango-web-1 bash
```

- **`-it`**: modo interactivo (`-i`) con una terminal (`-t`), para que se
  comporte como una consola normal en la que puedes escribir y ver el
  resultado.
- **`hellodjango-web-1`**: el nombre del contenedor que viste con `docker ps`.
- **`bash`**: el programa que se ejecuta dentro del contenedor — te abre una
  shell de Linux.

## 3. Ya adentro, corre los comandos directo

El `WORKDIR` del contenedor es `/app/src` (donde está `manage.py`), así que ya
no hace falta el prefijo `docker compose exec web`:

```bash
python manage.py migrate
python manage.py makemigrations
python manage.py dumpdata ecommerce --indent 4 --format json
python manage.py shell
```

## 4. Salir del contenedor

```bash
exit
```

Esto te regresa a tu terminal normal de Windows/PowerShell. El contenedor
sigue corriendo en segundo plano (no se apaga al salir de `bash`).
