from django.db import models
from accounts.models import Usuario


class Paciente(models.Model):
    """
    Modelo principal de paciente.
    Relacionado con el usuario del sistema mediante OneToOne.
    """

    TIPO_SANGRE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paciente_perfil',
        verbose_name='Usuario del sistema'
    )
    dni = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='DNI / Cédula'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        verbose_name='Género'
    )
    tipo_sangre = models.CharField(
        max_length=3,
        choices=TIPO_SANGRE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Tipo de sangre'
    )
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Correo electrónico')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.nombre} {self.apellido} (DNI: {self.dni})'

    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    def calcular_edad(self):
        from datetime import date
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad


class HistoriaClinica(models.Model):
    """
    Registro de historia clínica básica por paciente.
    Cada entrada representa una consulta o evento médico.
    """

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='historias',
        verbose_name='Paciente'
    )
    # medico se relacionará con la app de médicos (Desarrollador 2)
    # Por ahora se guarda como texto para no crear dependencia
    medico_nombre = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Médico tratante'
    )
    fecha = models.DateField(verbose_name='Fecha de consulta')
    motivo_consulta = models.TextField(verbose_name='Motivo de consulta')
    diagnostico = models.TextField(verbose_name='Diagnóstico')
    tratamiento = models.TextField(blank=True, null=True, verbose_name='Tratamiento')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historia Clínica'
        verbose_name_plural = 'Historias Clínicas'
        ordering = ['-fecha']

    def __str__(self):
        return f'Historia de {self.paciente.nombre_completo()} - {self.fecha}'
