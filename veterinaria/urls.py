from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('acceso-denegado/', views.acceso_denegado, name='acceso_denegado'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Usuarios
    path('usuarios/', views.usuario_lista, name='usuario_lista'),
    path('usuarios/nuevo/', views.usuario_crear, name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),

    # Mascotas
    path('mascotas/', views.mascota_lista, name='mascota_lista'),
    path('mascotas/nueva/', views.mascota_crear, name='mascota_crear'),
    path('mascotas/<int:pk>/editar/', views.mascota_editar, name='mascota_editar'),
    path('mascotas/<int:pk>/eliminar/', views.mascota_eliminar, name='mascota_eliminar'),

    # Clientes
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/nuevo/', views.cliente_crear, name='cliente_crear'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', views.cliente_eliminar, name='cliente_eliminar'),

    # Medicamentos
    path('medicamentos/', views.medicamento_lista, name='medicamento_lista'),
    path('medicamentos/nuevo/', views.medicamento_crear, name='medicamento_crear'),
    path('medicamentos/<int:pk>/editar/', views.medicamento_editar, name='medicamento_editar'),
    path('medicamentos/<int:pk>/eliminar/', views.medicamento_eliminar, name='medicamento_eliminar'),

    # Reportes
    path('reportes/medicamentos/', views.reporte_medicamentos, name='reporte_medicamentos'),
    path('reportes/clientes/', views.reporte_clientes, name='reporte_clientes'),
]