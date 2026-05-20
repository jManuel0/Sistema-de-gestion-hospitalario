from django.urls import path

from . import views

app_name = 'medicos'

urlpatterns = [
    path('', views.MedicoListView.as_view(), name='medico_lista'),
    path('nuevo/', views.MedicoCreateView.as_view(), name='medico_crear'),
    path('<int:pk>/', views.MedicoDetailView.as_view(), name='medico_detalle'),
    path('<int:pk>/editar/', views.MedicoUpdateView.as_view(), name='medico_editar'),
    path('<int:pk>/eliminar/', views.MedicoDeleteView.as_view(), name='medico_eliminar'),

    path('horarios/', views.HorarioListView.as_view(), name='horario_lista'),
    path('horarios/nuevo/', views.HorarioCreateView.as_view(), name='horario_crear'),
    path('horarios/<int:pk>/editar/', views.HorarioUpdateView.as_view(), name='horario_editar'),
    path('horarios/<int:pk>/eliminar/', views.HorarioDeleteView.as_view(), name='horario_eliminar'),

    path('citas/', views.CitaListView.as_view(), name='cita_lista'),
    path('citas/nueva/', views.CitaCreateView.as_view(), name='cita_crear'),
    path('citas/<int:pk>/', views.CitaDetailView.as_view(), name='cita_detalle'),
    path('citas/<int:pk>/editar/', views.CitaUpdateView.as_view(), name='cita_editar'),
    path('citas/<int:pk>/eliminar/', views.CitaDeleteView.as_view(), name='cita_eliminar'),
]

