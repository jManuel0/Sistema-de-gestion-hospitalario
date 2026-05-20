import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from pacientes.models import Paciente
from .models import Usuario


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesion personalizado."""

    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Contrasena',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contrasena',
        })
    )


class RegistroForm(UserCreationForm):
    """Formulario de registro de nuevos usuarios."""

    first_name = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    email = forms.EmailField(
        label='Correo electronico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    telefono = forms.CharField(
        label='Telefono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefono'})
    )
    dni = forms.CharField(
        label='DNI / Cedula',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numero de documento',
            'data-paciente-field': 'true',
        })
    )
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'data-paciente-field': 'true',
        })
    )
    genero = forms.ChoiceField(
        label='Genero',
        choices=[('', 'Seleccione')] + Paciente.GENERO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-paciente-field': 'true',
        })
    )
    rol = forms.ChoiceField(
        label='Rol',
        choices=Usuario.ROLES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_rol'})
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email', 'telefono', 'rol',
            'dni', 'fecha_nacimiento', 'genero', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contrasena'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contrasena'})
        self.fields['username'].label = 'Usuario'
        self.fields['password1'].label = 'Contrasena'
        self.fields['password2'].label = 'Confirmar contrasena'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electronico.')
        return email

    def clean_dni(self):
        dni = (self.cleaned_data.get('dni') or '').strip().upper()
        rol = self.data.get('rol') or self.cleaned_data.get('rol')

        if rol == Usuario.ROL_PACIENTE:
            if not dni:
                raise forms.ValidationError('El DNI / cedula es obligatorio para pacientes.')
            if not re.fullmatch(r'[A-Z0-9.-]{5,20}', dni):
                raise forms.ValidationError('Use solo letras, numeros, puntos o guiones. Minimo 5 caracteres.')
            if Paciente.objects.filter(dni__iexact=dni).exists():
                raise forms.ValidationError('Ya existe un paciente con este DNI / cedula.')

        return dni

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')

        if rol == Usuario.ROL_PACIENTE:
            if not cleaned_data.get('telefono'):
                self.add_error('telefono', 'El telefono es obligatorio para pacientes.')
            if not cleaned_data.get('fecha_nacimiento'):
                self.add_error('fecha_nacimiento', 'La fecha de nacimiento es obligatoria para pacientes.')
            if not cleaned_data.get('genero'):
                self.add_error('genero', 'El genero es obligatorio para pacientes.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit and user.rol == Usuario.ROL_PACIENTE:
            Paciente.objects.get_or_create(
                usuario=user,
                defaults={
                    'dni': self.cleaned_data['dni'],
                    'nombre': user.first_name,
                    'apellido': user.last_name,
                    'fecha_nacimiento': self.cleaned_data['fecha_nacimiento'],
                    'genero': self.cleaned_data['genero'],
                    'telefono': user.telefono,
                    'email': user.email,
                    'activo': True,
                }
            )

        return user


class EditarUsuarioForm(forms.ModelForm):
    """Formulario para editar perfil de usuario."""

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electronico',
            'telefono': 'Telefono',
        }
