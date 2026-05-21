# Desarrollador 3 - Dashboard y Reportes

## Funcionalidades agregadas

Se agrego una nueva app Django llamada `dashboard`, separada de los modulos existentes de autenticacion, pacientes, medicos y citas.

Incluye:

- Vista principal en `/dashboard/`.
- Cards con resumen general del sistema.
- Total de pacientes, medicos y citas del periodo filtrado.
- Citas del dia.
- Pacientes activos e inactivos.
- Estados de citas: pendientes, confirmadas, completadas y canceladas.
- Grafico Chart.js de citas por especialidad medica.
- Grafico Chart.js de pacientes nuevos por mes.
- Filtros por fecha: hoy, esta semana, este mes y rango manual.
- Exportacion de estadisticas a Excel.
- Exportacion de estadisticas a PDF.

## Archivos principales

- `dashboard/services.py`: consultas estadisticas y filtros de fecha.
- `dashboard/views.py`: vistas del dashboard y endpoints de exportacion.
- `dashboard/reports.py`: generacion de archivos Excel y PDF.
- `dashboard/urls.py`: rutas propias de la app.
- `templates/dashboard/home.html`: interfaz responsive con Bootstrap y Chart.js.

## Como ejecutar el dashboard

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Aplicar migraciones existentes:

```bash
python manage.py migrate
```

3. Levantar el servidor:

```bash
python manage.py runserver
```

4. Abrir:

```text
http://127.0.0.1:8000/dashboard/
```

El acceso esta restringido a usuarios autenticados con rol `admin` o `medico`.

## Como usar los filtros

En la parte superior del dashboard se puede seleccionar:

- `Hoy`
- `Esta semana`
- `Este mes`
- `Rango manual`

Cuando se usa rango manual, seleccionar `Fecha inicio` y `Fecha fin`, luego pulsar `Aplicar`.

## Como usar los reportes

Desde `/dashboard/`, usar los botones:

- `Excel`: descarga `dashboard_estadisticas.xlsx`.
- `PDF`: descarga `dashboard_estadisticas.pdf`.

Los reportes respetan los filtros aplicados en pantalla e incluyen resumen general y citas por especialidad.

## Dependencias nuevas

No se agregaron dependencias nuevas al proyecto.

Se reutilizaron dependencias ya presentes en `requirements.txt`:

- `openpyxl` para Excel.
- `reportlab` para PDF.

Chart.js se carga desde CDN en el template del dashboard.
