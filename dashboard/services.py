from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from medicos.models import Cita, Medico
from pacientes.models import Paciente


PERIOD_LABELS = {
    'hoy': 'Hoy',
    'semana': 'Esta semana',
    'mes': 'Este mes',
    'rango': 'Rango personalizado',
}


def parse_dashboard_filters(params):
    """Normaliza los filtros de fecha usados por el dashboard y sus reportes."""
    today = timezone.localdate()
    period = params.get('periodo') or 'mes'

    if period == 'hoy':
        start_date = today
        end_date = today
    elif period == 'semana':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'rango':
        start_date = _parse_date(params.get('fecha_inicio')) or today
        end_date = _parse_date(params.get('fecha_fin')) or start_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date
    else:
        period = 'mes'
        start_date = today.replace(day=1)
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)

    return {
        'periodo': period,
        'periodo_label': PERIOD_LABELS[period],
        'fecha_inicio': start_date,
        'fecha_fin': end_date,
    }


def get_dashboard_statistics(filters):
    """Agrupa las metricas del sistema sin modificar los modulos funcionales."""
    start_date = filters['fecha_inicio']
    end_date = filters['fecha_fin']

    citas_periodo = Cita.objects.filter(fecha__range=(start_date, end_date))
    pacientes_periodo = Paciente.objects.filter(fecha_registro__date__range=(start_date, end_date))
    today = timezone.localdate()

    pacientes_activos = Paciente.objects.filter(activo=True).count()
    pacientes_inactivos = Paciente.objects.filter(activo=False).count()
    total_pacientes = Paciente.objects.count()
    total_medicos = Medico.objects.count()

    citas_por_estado = {
        row['estado']: row['total']
        for row in citas_periodo.values('estado').annotate(total=Count('id'))
    }

    citas_especialidad = list(
        citas_periodo
        .values('medico__especialidad')
        .annotate(total=Count('id'))
        .order_by('medico__especialidad')
    )

    pacientes_por_mes = list(
        Paciente.objects
        .filter(fecha_registro__date__range=(start_date, end_date))
        .annotate(mes=TruncMonth('fecha_registro'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    return {
        'resumen': {
            'total_pacientes': total_pacientes,
            'total_medicos': total_medicos,
            'total_citas': citas_periodo.count(),
            'citas_hoy': Cita.objects.filter(fecha=today).count(),
            'pacientes_activos': pacientes_activos,
            'pacientes_inactivos': pacientes_inactivos,
            'pacientes_nuevos': pacientes_periodo.count(),
            'medicos_activos': Medico.objects.filter(activo=True).count(),
            'citas_pendientes': citas_por_estado.get(Cita.ESTADO_PENDIENTE, 0),
            'citas_confirmadas': citas_por_estado.get(Cita.ESTADO_CONFIRMADA, 0),
            'citas_completadas': citas_por_estado.get(Cita.ESTADO_COMPLETADA, 0),
            'citas_canceladas': citas_por_estado.get(Cita.ESTADO_CANCELADA, 0),
        },
        'charts': {
            'citas_especialidad': {
                'labels': [row['medico__especialidad'] or 'Sin especialidad' for row in citas_especialidad],
                'data': [row['total'] for row in citas_especialidad],
            },
            'pacientes_mes': {
                'labels': [row['mes'].strftime('%Y-%m') for row in pacientes_por_mes],
                'data': [row['total'] for row in pacientes_por_mes],
            },
        },
    }


def _parse_date(value):
    if not value:
        return None
    try:
        return timezone.datetime.fromisoformat(value).date()
    except ValueError:
        return None
