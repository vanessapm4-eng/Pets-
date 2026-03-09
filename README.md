# PETS S.A. Es un Sistema de Gestión Veterinaria
Centro Veterinario de Cartagena, Colombia

##  Descripción
Aplicación web desarrollada con Django para gestionar 
la información del centro veterinario PETS S.A.

##  Arquitectura por capas
- **Capa 1 - Modelos** → `models.py`
- **Capa 2 - Formularios** → `forms.py`
- **Capa 3 - Servicios** → `services.py`
- **Capa 4 - Vistas** → `views.py`
- **Capa 5 - Rutas** → `urls.py`
- **Capa 6 - Templates** → `templates/`

## Tecnologías
- Python 3.13
- Django 6.0.3
- SQLite
- HTML/CSS

## Instalación
```bash
pip install django
python manage.py migrate
python manage.py runserver
```

## Módulos
- Mascotas — CRUD completo
- Clientes — CRUD completo
- Medicamentos — CRUD completo
- Reporte de clientes
- Reporte de medicamentos
