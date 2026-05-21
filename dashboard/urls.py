from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('exportar/excel/', views.export_statistics_excel, name='export_excel'),
    path('exportar/pdf/', views.export_statistics_pdf, name='export_pdf'),
]
