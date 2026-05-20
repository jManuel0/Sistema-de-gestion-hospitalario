import re
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from pacientes.models import Paciente


class Medico(models.Model):
    ESPECIALIDAD_MEDICINA_GENERAL = 'Medicina General'
    ESPECIALIDAD_PEDIATRIA = 'Pediatria'
    ESPECIALIDAD_CARDIOLOGIA = 'Cardiologia'
    ESPECIALIDAD_DERMATOLOGIA = 'Dermatologia'
    ESPECIALIDAD_NEUROLOGIA = 'Neurologia'
    ESPECIALIDAD_ODONTOLOGIA = 'Odontologia'
    ESPECIALIDAD_PSICOLOGIA = 'Psicologia'
    ESPECIALIDAD_ORTOPEDIA = 'Ortopedia'
    ESPECIALIDAD_GINECOLOGIA = 'Ginecologia'
    ESPECIALIDAD_OTRA = 'Otra'

    ESPECIALIDADES = [
        (ESPECIALIDAD_MEDICINA_GENERAL, 'Medicina General'),
        (ESPECIALIDAD_PEDIATRIA, 'Pediatria'),
        (ESPECIALIDAD_CARDIOLOGIA, 'Cardiologia'),
        (ESPECIALIDAD_DERMATOLOGIA, 'Dermatologia'),
        (ESPECIALIDAD_NEUROLOGIA, 'Neurologia'),
        (ESPECIALIDAD_ODONTOLOGIA, 'Odontologia'),
        (ESPECIALIDAD_PSICOLOGIA, 'Psicologia'),
        (ESPECIALIDAD_ORTOPEDIA, 'Ortopedia'),
        (ESPECIALIDAD_GINECOLOGIA, 'Ginecologia'),
        (ESPECIALIDAD_OTRA, 'Otra'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medico_perfil',
        verbose_name='Usuario medico'
    )
    especialidad = models.CharField(
        max_length=120,
        choices=ESPECIALIDADES,
        default=ESPECIALIDAD_MEDICINA_GENERAL,
        verbose_name='Especialidad'
    )
    telefono = models.CharField(max_length=20, verbose_name='Telefono')
    numero_licencia = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Numero de licencia'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')

    class Meta:
        verbose_name = 'Medico'
        verbose_name_plural = 'Medicos'
        ordering = ['usuario__last_name', 'usuario__first_name', 'especialidad']

    def __str__(self):
        return f'{self.nombre_completo()} - {self.especialidad}'

    def nombre_completo(self):
        return self.usuario.get_full_name() or self.usuario.username

    def horarios_activos(self):
        return self.horarios.filter(activo=True).order_by('dia_semana', 'hora_inicio')

    def clean(self):
        super().clean()
        if self.usuario_id:
            rol = getattr(self.usuario, 'rol', None)
            if rol != 'medico':
                raise ValidationError({'usuario': 'Solo se pueden asociar usuarios con rol medico.'})

        if self.telefono and not re.fullmatch(r'[\d\s()+-]{7,20}', self.telefono):
            raise ValidationError({'telefono': 'Ingrese un telefono valido.'})


class Horario(models.Model):
    LUNES = 0
    MARTES = 1
    MIERCOLES = 2
    JUEVES = 3
    VIERNES = 4
    SABADO = 5
    DOMINGO = 6

    DIAS_SEMANA = [
        (LUNES, 'Lunes'),
        (MARTES, 'Martes'),
        (MIERCOLES, 'Miercoles'),
        (JUEVES, 'Jueves'),
        (VIERNES, 'Viernes'),
        (SABADO, 'Sabado'),
        (DOMINGO, 'Domingo'),
    ]

    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name='horarios',
        verbose_name='Medico'
    )
    dia_semana = models.PositiveSmallIntegerField(choices=DIAS_SEMANA, verbose_name='Dia de la semana')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['medico', 'dia_semana', 'hora_inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['medico', 'dia_semana', 'hora_inicio', 'hora_fin'],
                name='horario_unico_por_medico_dia_rango'
            )
        ]

    def __str__(self):
        return f'{self.medico} - {self.get_dia_semana_display()} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}'

    def rango_legible(self):
        return f'{self.hora_inicio.strftime("%I:%M %p")} a {self.hora_fin.strftime("%I:%M %p")}'

    def clean(self):
        super().clean()
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError({'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'})

        if not all([self.medico_id, self.dia_semana is not None, self.hora_inicio, self.hora_fin]):
            return

        solapados = Horario.objects.filter(
            medico=self.medico,
            dia_semana=self.dia_semana,
            activo=True,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        )
        if self.pk:
            solapados = solapados.exclude(pk=self.pk)

        if self.activo and solapados.exists():
            raise ValidationError('El horario se superpone con otro horario activo del mismo medico.')


class Cita(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_CONFIRMADA = 'confirmada'
    ESTADO_CANCELADA = 'cancelada'
    ESTADO_COMPLETADA = 'completada'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_CANCELADA, 'Cancelada'),
        (ESTADO_COMPLETADA, 'Completada'),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name='Paciente'
    )
    medico = models.ForeignKey(
        Medico,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='Medico'
    )
    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(verbose_name='Hora')
    motivo = models.TextField(verbose_name='Motivo')
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        verbose_name='Estado'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha', '-hora']
        indexes = [
            models.Index(fields=['fecha', 'hora']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'{self.paciente.nombre_completo()} con {self.medico.nombre_completo()} - {self.fecha} {self.hora:%H:%M}'

    @property
    def fecha_hora(self):
        return datetime.combine(self.fecha, self.hora)

    def horarios_del_dia(self):
        if not self.medico_id or not self.fecha:
            return Horario.objects.none()
        return Horario.objects.filter(
            medico=self.medico,
            dia_semana=self.fecha.weekday(),
            activo=True,
        ).order_by('hora_inicio')

    def dias_disponibles_medico(self):
        if not self.medico_id:
            return ''
        dias = (
            Horario.objects
            .filter(medico=self.medico, activo=True)
            .order_by('dia_semana')
            .values_list('dia_semana', flat=True)
            .distinct()
        )
        nombres = dict(Horario.DIAS_SEMANA)
        return ', '.join(nombres[dia] for dia in dias)

    def clean(self):
        super().clean()
        if not all([self.paciente_id, self.medico_id, self.fecha, self.hora]):
            return

        fecha_hora = timezone.make_aware(self.fecha_hora, timezone.get_current_timezone())
        if fecha_hora < timezone.now():
            raise ValidationError('No se pueden registrar citas en una fecha u hora pasada.')

        if not self.medico.activo:
            raise ValidationError({'medico': 'El medico seleccionado no esta activo.'})

        dia_semana = self.fecha.weekday()
        horarios_medico = Horario.objects.filter(medico=self.medico, activo=True)
        if not horarios_medico.exists():
            raise ValidationError({
                'medico': 'El medico seleccionado aun no tiene horarios configurados. Seleccione otro medico o intente mas tarde.'
            })

        horarios_dia = self.horarios_del_dia()
        if not horarios_dia.exists():
            dias = self.dias_disponibles_medico() or 'sin dias configurados'
            raise ValidationError({
                'fecha': f'El medico no atiende ese dia. Dias disponibles: {dias}.'
            })

        disponible = horarios_dia.filter(hora_inicio__lte=self.hora, hora_fin__gt=self.hora).exists()
        if not disponible:
            rangos = ', '.join(h.rango_legible() for h in horarios_dia)
            raise ValidationError({
                'hora': f'La hora seleccionada esta fuera del horario disponible. El medico atiende ese dia de {rangos}.'
            })

        if self.estado != self.ESTADO_CANCELADA:
            citas_activas = Cita.objects.exclude(estado=self.ESTADO_CANCELADA)
            if self.pk:
                citas_activas = citas_activas.exclude(pk=self.pk)

            if citas_activas.filter(medico=self.medico, fecha=self.fecha, hora=self.hora).exists():
                raise ValidationError({
                    'hora': 'Ese horario ya fue reservado con este medico. Seleccione otra hora dentro del horario disponible.'
                })

            if citas_activas.filter(paciente=self.paciente, fecha=self.fecha, hora=self.hora).exists():
                raise ValidationError({
                    'hora': 'Ya tienes una cita registrada en esa misma fecha y hora.'
                })
