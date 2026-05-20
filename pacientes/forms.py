from django import forms
from .models import Paciente, HistoriaClinica


class PacienteForm(forms.ModelForm):
    """Formulario para crear y editar pacientes."""

    class Meta:
        model = Paciente
        fields = [
            'dni', 'nombre', 'apellido', 'fecha_nacimiento',
            'genero', 'tipo_sangre', 'telefono', 'email',
            'direccion', 'activo'
        ]
        widgets = {
            'dni': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de cédula o DNI'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del paciente'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del paciente'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'tipo_sangre': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección del paciente'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'dni': 'DNI / Cédula',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'genero': 'Género',
            'tipo_sangre': 'Tipo de sangre',
            'telefono': 'Teléfono',
            'email': 'Correo electrónico',
            'direccion': 'Dirección',
            'activo': 'Paciente activo',
        }

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        qs = Paciente.objects.filter(dni=dni)
        # Excluir el propio registro al editar
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un paciente con este DNI.')
        return dni

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Paciente.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un paciente con este correo electrónico.')
        return email


class HistoriaClinicaForm(forms.ModelForm):
    """Formulario para registrar entradas de historia clínica."""

    class Meta:
        model = HistoriaClinica
        fields = ['fecha', 'medico_nombre', 'motivo_consulta', 'diagnostico', 'tratamiento', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'medico_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del médico tratante'
            }),
            'motivo_consulta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa el motivo de la consulta'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnóstico médico'
            }),
            'tratamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tratamiento indicado'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales'
            }),
        }
        labels = {
            'fecha': 'Fecha de consulta',
            'medico_nombre': 'Médico tratante',
            'motivo_consulta': 'Motivo de consulta',
            'diagnostico': 'Diagnóstico',
            'tratamiento': 'Tratamiento',
            'observaciones': 'Observaciones',
        }


class BuscarPacienteForm(forms.Form):
    """Formulario de búsqueda de pacientes."""

    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, apellido o DNI...',
        })
    )
    activo = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[('', 'Todos'), ('1', 'Activos'), ('0', 'Inactivos')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
