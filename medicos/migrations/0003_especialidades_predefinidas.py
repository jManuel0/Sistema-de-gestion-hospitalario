from django.db import migrations, models


def normalizar_especialidades(apps, schema_editor):
    Medico = apps.get_model('medicos', 'Medico')
    Medico.objects.filter(especialidad__in=['', 'Por definir', None]).update(especialidad='Medicina General')


class Migration(migrations.Migration):

    dependencies = [
        ('medicos', '0002_crear_perfiles_medicos_existentes'),
    ]

    operations = [
        migrations.RunPython(normalizar_especialidades, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='medico',
            name='especialidad',
            field=models.CharField(
                choices=[
                    ('Medicina General', 'Medicina General'),
                    ('Pediatria', 'Pediatria'),
                    ('Cardiologia', 'Cardiologia'),
                    ('Dermatologia', 'Dermatologia'),
                    ('Neurologia', 'Neurologia'),
                    ('Odontologia', 'Odontologia'),
                    ('Psicologia', 'Psicologia'),
                    ('Ortopedia', 'Ortopedia'),
                    ('Ginecologia', 'Ginecologia'),
                    ('Otra', 'Otra'),
                ],
                default='Medicina General',
                max_length=120,
                verbose_name='Especialidad'
            ),
        ),
    ]
