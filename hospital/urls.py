"""URL configuration for hospital project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('pacientes/', include('pacientes.urls', namespace='pacientes')),
    path('medicos/', include('medicos.urls', namespace='medicos')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('', lambda request: redirect('pacientes:lista'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
