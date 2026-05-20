from django.conf import settings
from django.core.mail import send_mail


def enviar_confirmacion_cita(cita):
    email = cita.paciente.email or getattr(cita.paciente.usuario, 'email', '')
    if not email:
        return 0

    asunto = 'Confirmacion de cita medica'
    mensaje = (
        f'Su cita ha sido registrada.\n\n'
        f'Medico: {cita.medico.nombre_completo()}\n'
        f'Especialidad: {cita.medico.especialidad}\n'
        f'Fecha: {cita.fecha:%d/%m/%Y}\n'
        f'Hora: {cita.hora:%H:%M}\n'
        f'Estado: {cita.get_estado_display()}\n'
    )
    return send_mail(
        asunto,
        mensaje,
        getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@hospital.local'),
        [email],
        fail_silently=True,
    )

