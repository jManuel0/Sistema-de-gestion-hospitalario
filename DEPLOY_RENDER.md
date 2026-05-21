# Despliegue en Render

## Variables de entorno

Configurar estas variables en el servicio web de Render:

```text
SECRET_KEY=clave-secreta-segura
DEBUG=False
ALLOWED_HOSTS=nombre-del-servicio.onrender.com
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DATABASE
CSRF_TRUSTED_ORIGINS=https://nombre-del-servicio.onrender.com
```

No subir valores reales de produccion al repositorio. Usar `.env.example` como plantilla.

## Base de datos PostgreSQL

1. Crear una base PostgreSQL en Render.
2. Copiar el valor de `External Database URL` o `Internal Database URL`.
3. Guardarlo en la variable `DATABASE_URL` del servicio web.

El proyecto usa `dj-database-url` para leer `DATABASE_URL`. Si esa variable no existe, Django conserva SQLite para desarrollo local.

## Servicio web en Render

Crear un nuevo Web Service conectado al repositorio y configurar:

```text
Environment: Python
Build Command: ./build.sh
Start Command: gunicorn hospital.wsgi
```

El archivo `.python-version` fija Python 3.12.4 para mantener compatibilidad con las dependencias actuales, incluyendo `Pillow==10.3.0` y `psycopg2-binary`.

Si Render sigue intentando construir con Python 3.14, agregar tambien esta variable de entorno en el panel del servicio:

```text
PYTHON_VERSION=3.12.4
```

Render tambien puede leer el `Procfile`:

```text
web: gunicorn hospital.wsgi
```

## Archivos estaticos

WhiteNoise sirve los archivos estaticos en produccion. El script `build.sh` ejecuta:

```bash
python manage.py collectstatic --no-input
```

Bootstrap, Bootstrap Icons y Chart.js se cargan desde CDN en los templates existentes. Los archivos locales dentro de `static/` se recopilan en `staticfiles/`.

## Comandos importantes

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Validar configuracion:

```bash
python manage.py check
```

Aplicar migraciones:

```bash
python manage.py migrate
```

Recopilar estaticos:

```bash
python manage.py collectstatic --no-input
```

## Desarrollo local

Para trabajar localmente, crear un archivo `.env` basado en `.env.example`:

```text
SECRET_KEY=django-insecure-local
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

Si no defines `DATABASE_URL`, el proyecto usa `db.sqlite3` como antes.
