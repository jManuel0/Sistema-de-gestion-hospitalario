# Sistema de Gestión Hospitalaria - MediSystem

Aplicación web desarrollada con Django para la gestión de citas médicas, pacientes y médicos.

---

## Desarrollador 1 — Rama: `dev-dev1`

Responsable de:
- Setup del proyecto Django
- App `accounts`: autenticación, roles y gestión de usuarios
- App `pacientes`: CRUD de pacientes, historia clínica y exportaciones

---

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd hospital

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Ejecutar servidor
python manage.py runserver
```

Acceder en: http://127.0.0.1:8000

---

## Estructura del proyecto

```
hospital/
├── hospital/           # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/           # Autenticación y usuarios
│   ├── models.py       # Modelo Usuario (AbstractUser + rol)
│   ├── views.py        # Login, logout, registro, perfil
│   ├── forms.py
│   ├── decorators.py   # Control de acceso por rol
│   └── urls.py
├── pacientes/          # Gestión de pacientes
│   ├── models.py       # Paciente, HistoriaClinica
│   ├── views.py        # CRUD + exportaciones
│   ├── forms.py
│   ├── utils.py        # Generación Excel y PDF
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── accounts/
│   └── pacientes/
├── manage.py
└── requirements.txt
```

---

## Modelos principales

### `accounts.Usuario`
Extiende `AbstractUser` con campo `rol` (admin, medico, paciente) y `activo`.

### `pacientes.Paciente`
Campos: `dni`, `nombre`, `apellido`, `fecha_nacimiento`, `genero`, `tipo_sangre`, `telefono`, `email`, `direccion`, `activo`.

### `pacientes.HistoriaClinica`
FK a `Paciente`. Campos: `fecha`, `medico_nombre`, `motivo_consulta`, `diagnostico`, `tratamiento`, `observaciones`.

---

## Rutas principales

| Ruta | Descripción |
|------|-------------|
| `/accounts/login/` | Inicio de sesión |
| `/accounts/registro/` | Registro de usuario |
| `/accounts/perfil/` | Perfil del usuario |
| `/accounts/usuarios/` | Lista de usuarios (admin) |
| `/pacientes/` | Lista de pacientes |
| `/pacientes/nuevo/` | Crear paciente |
| `/pacientes/<pk>/` | Detalle del paciente |
| `/pacientes/<pk>/editar/` | Editar paciente |
| `/pacientes/<pk>/eliminar/` | Eliminar paciente |
| `/pacientes/<pk>/historia/nueva/` | Nueva entrada clínica |
| `/pacientes/exportar/excel/` | Exportar a Excel |
| `/pacientes/<pk>/exportar/pdf/` | Exportar historia a PDF |

---

## Flujo Git

```bash
# Rama de trabajo
git checkout dev-dev1

# Integrar cambios al equipo
git checkout dev
git merge dev-dev1
git push origin dev
```
