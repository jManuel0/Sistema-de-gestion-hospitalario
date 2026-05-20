from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Usuario
from .models import Medico


def crear_perfil_medico_si_falta(usuario):
    if getattr(usuario, 'rol', None) != 'medico':
        return None

    medico, _ = Medico.objects.get_or_create(
        usuario=usuario,
        defaults={
            'especialidad': Medico.ESPECIALIDAD_MEDICINA_GENERAL,
            'telefono': usuario.telefono or '0000000',
            'numero_licencia': f'AUTO-{usuario.pk}',
            'activo': getattr(usuario, 'activo', True),
        }
    )
    return medico


@receiver(post_save, sender=Usuario)
def sincronizar_perfil_medico(sender, instance, **kwargs):
    crear_perfil_medico_si_falta(instance)
