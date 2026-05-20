from django.contrib import admin

from .models import Cita, Horario, Medico


class HorarioInline(admin.TabularInline):
    model = Horario
    extra = 0


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'especialidad', 'telefono', 'numero_licencia', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'especialidad']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'usuario__username', 'especialidad', 'numero_licencia']
    readonly_fields = ['fecha_creacion']
    inlines = [HorarioInline]


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['medico', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
    list_filter = ['dia_semana', 'activo', 'medico__especialidad']
    search_fields = ['medico__usuario__first_name', 'medico__usuario__last_name', 'medico__numero_licencia']


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'fecha', 'hora', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'fecha', 'medico__especialidad']
    search_fields = [
        'paciente__nombre',
        'paciente__apellido',
        'paciente__dni',
        'medico__usuario__first_name',
        'medico__usuario__last_name',
        'motivo',
    ]
    readonly_fields = ['fecha_creacion']
    date_hierarchy = 'fecha'

