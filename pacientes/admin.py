from django.contrib import admin
from .models import Paciente, HistoriaClinica


class HistoriaClinicaInline(admin.TabularInline):
    model = HistoriaClinica
    extra = 0
    fields = ['fecha', 'medico', 'medico_nombre', 'motivo_consulta', 'diagnostico']
    readonly_fields = ['fecha_creacion']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['dni', 'nombre_completo', 'fecha_nacimiento', 'telefono', 'email', 'activo', 'fecha_registro']
    list_filter = ['activo', 'genero', 'tipo_sangre']
    search_fields = ['dni', 'nombre', 'apellido', 'email']
    ordering = ['apellido', 'nombre']
    inlines = [HistoriaClinicaInline]
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']

    fieldsets = (
        ('Información personal', {
            'fields': ('dni', 'nombre', 'apellido', 'fecha_nacimiento', 'genero', 'tipo_sangre')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion')
        }),
        ('Sistema', {
            'fields': ('usuario', 'activo', 'fecha_registro', 'fecha_actualizacion')
        }),
    )


@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'fecha', 'medico', 'medico_nombre', 'motivo_consulta']
    list_filter = ['fecha']
    search_fields = ['paciente__nombre', 'paciente__apellido', 'paciente__dni', 'medico__usuario__first_name', 'medico__usuario__last_name', 'diagnostico']
    ordering = ['-fecha']
    readonly_fields = ['fecha_creacion']
