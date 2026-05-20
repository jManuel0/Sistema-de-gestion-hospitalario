from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado con soporte de roles.
    Extiende AbstractUser para mantener toda la funcionalidad
    de autenticación de Django.
    """

    ROL_ADMIN = 'admin'
    ROL_MEDICO = 'medico'
    ROL_PACIENTE = 'paciente'

    ROLES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_MEDICO, 'Médico'),
        (ROL_PACIENTE, 'Paciente'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default=ROL_PACIENTE,
        verbose_name='Rol'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Usuario activo'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_rol_display()})'

    def es_admin(self):
        return self.rol == self.ROL_ADMIN

    def es_medico(self):
        return self.rol == self.ROL_MEDICO

    def es_paciente(self):
        return self.rol == self.ROL_PACIENTE
