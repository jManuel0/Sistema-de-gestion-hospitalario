from django import forms
from django.db.models import Q

from accounts.models import Usuario
from pacientes.models import Paciente
from .models import Cita, Horario, Medico


BOOTSTRAP_TEXT_WIDGETS = (
    forms.TextInput,
    forms.EmailInput,
    forms.NumberInput,
    forms.DateInput,
    forms.TimeInput,
    forms.Textarea,
)


def aplicar_bootstrap(form):
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault('class', 'form-check-input')
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault('class', 'form-select')
        elif isinstance(widget, BOOTSTRAP_TEXT_WIDGETS):
            widget.attrs.setdefault('class', 'form-control')


class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['usuario', 'especialidad', 'telefono', 'numero_licencia', 'activo']
        widgets = {
            'especialidad': forms.Select(),
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej: +57 300 123 4567'}),
            'numero_licencia': forms.TextInput(attrs={'placeholder': 'Registro o licencia profesional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        usuarios_asignados = Medico.objects.values_list('usuario_id', flat=True)
        queryset = Usuario.objects.filter(rol='medico', activo=True)
        if self.instance.pk:
            queryset = queryset.filter(Q(pk=self.instance.usuario_id) | ~Q(pk__in=usuarios_asignados))
        else:
            queryset = queryset.exclude(pk__in=usuarios_asignados)
        self.fields['usuario'].queryset = queryset.order_by('first_name', 'last_name', 'username')
        self.fields['especialidad'].required = True
        aplicar_bootstrap(self)

    def clean_numero_licencia(self):
        licencia = self.cleaned_data['numero_licencia'].strip().upper()
        qs = Medico.objects.filter(numero_licencia__iexact=licencia)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un medico con esta licencia.')
        return licencia


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['medico', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['medico'].queryset = Medico.objects.filter(activo=True).select_related('usuario')
        if user and getattr(user, 'rol', None) == 'medico' and hasattr(user, 'medico_perfil'):
            self.fields['medico'].queryset = Medico.objects.filter(pk=user.medico_perfil.pk)
            self.fields['medico'].initial = user.medico_perfil
            self.fields['medico'].disabled = True
        aplicar_bootstrap(self)


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'medico', 'fecha', 'hora', 'motivo', 'estado', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Motivo principal de la consulta'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observaciones internas u opcionales'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).order_by('apellido', 'nombre')
        self.fields['medico'].queryset = Medico.objects.filter(activo=True).select_related('usuario')

        if user and getattr(user, 'rol', None) == 'medico' and hasattr(user, 'medico_perfil'):
            self.fields['medico'].queryset = Medico.objects.filter(pk=user.medico_perfil.pk)
            self.fields['medico'].initial = user.medico_perfil
            self.fields['medico'].disabled = True

        if user and getattr(user, 'rol', None) == 'paciente' and hasattr(user, 'paciente_perfil'):
            self.fields['paciente'].queryset = Paciente.objects.filter(pk=user.paciente_perfil.pk)
            self.fields['paciente'].initial = user.paciente_perfil
            self.fields['paciente'].disabled = True

        aplicar_bootstrap(self)


class PacienteCitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['medico', 'fecha', 'hora', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe brevemente el motivo de la consulta'}),
        }
        labels = {
            'medico': 'Medico',
            'fecha': 'Fecha',
            'hora': 'Hora',
            'motivo': 'Motivo',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['medico'].queryset = Medico.objects.filter(activo=True).select_related('usuario')
        aplicar_bootstrap(self)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and getattr(self.user, 'rol', None) == 'paciente' and hasattr(self.user, 'paciente_perfil'):
            self.instance.paciente = self.user.paciente_perfil
        return cleaned_data

    def save(self, commit=True):
        cita = super().save(commit=False)
        if self.user and getattr(self.user, 'rol', None) == 'paciente' and hasattr(self.user, 'paciente_perfil'):
            cita.paciente = self.user.paciente_perfil
        if commit:
            cita.save()
        return cita


class BuscarMedicoForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre, especialidad o licencia...'
        })
    )
    activo = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[('', 'Todos'), ('1', 'Activos'), ('0', 'Inactivos')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class BuscarCitaForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Paciente, medico o motivo...'
        })
    )
    fecha = forms.DateField(
        required=False,
        label='Fecha',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    medico = forms.ModelChoiceField(
        required=False,
        queryset=Medico.objects.none(),
        label='Medico',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[('', 'Todos')] + Cita.ESTADOS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Medico.objects.filter(activo=True).select_related('usuario')
        if user and getattr(user, 'rol', None) == 'medico' and hasattr(user, 'medico_perfil'):
            queryset = queryset.filter(pk=user.medico_perfil.pk)
        self.fields['medico'].queryset = queryset
