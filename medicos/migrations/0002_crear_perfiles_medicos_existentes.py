from django.db import migrations


def crear_perfiles_medicos(apps, schema_editor):
    Usuario = apps.get_model('accounts', 'Usuario')
    Medico = apps.get_model('medicos', 'Medico')

    for usuario in Usuario.objects.filter(rol='medico'):
        Medico.objects.get_or_create(
            usuario=usuario,
            defaults={
                'especialidad': 'Por definir',
                'telefono': usuario.telefono or '0000000',
                'numero_licencia': f'AUTO-{usuario.pk}',
                'activo': usuario.activo,
            }
        )


def revertir_perfiles_automaticos(apps, schema_editor):
    Medico = apps.get_model('medicos', 'Medico')
    Medico.objects.filter(numero_licencia__startswith='AUTO-').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('medicos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_perfiles_medicos, revertir_perfiles_automaticos),
    ]
