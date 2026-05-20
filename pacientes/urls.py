from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    # Lista y búsqueda
    path('', views.lista_pacientes, name='lista'),

    # CRUD pacientes
    path('nuevo/', views.crear_paciente, name='crear'),
    path('<int:pk>/', views.detalle_paciente, name='detalle'),
    path('<int:pk>/editar/', views.editar_paciente, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_paciente, name='eliminar'),

    # Historia clínica
    path('<int:pk>/historia/nueva/', views.agregar_historia, name='agregar_historia'),
    path('<int:pk>/historia/<int:historia_pk>/editar/', views.editar_historia, name='editar_historia'),
    path('<int:pk>/historia/<int:historia_pk>/eliminar/', views.eliminar_historia, name='eliminar_historia'),

    # Exportaciones
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('<int:pk>/exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
]
