from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
    path('usuarios/<int:pk>/toggle/', views.toggle_usuario_view, name='toggle_usuario'),
]
