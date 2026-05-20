from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistroForm, EditarUsuarioForm
from .models import Usuario
from .decorators import solo_admin


def redireccion_por_rol(user):
    if getattr(user, 'rol', None) == 'paciente':
        return 'medicos:cita_lista'
    return 'pacientes:lista'


def login_view(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect(redireccion_por_rol(request.user))

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if not user.activo:
                messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
                return render(request, 'accounts/login.html', {'form': form})
            login(request, user)
            messages.success(request, f'Bienvenido, {user.get_full_name() or user.username}.')
            next_url = request.GET.get('next') or redireccion_por_rol(user)
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Vista de cierre de sesión."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('accounts:login')


def registro_view(request):
    """Vista de registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect(redireccion_por_rol(request.user))

    form = RegistroForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Cuenta creada exitosamente. Bienvenido, {user.get_full_name() or user.username}.')
            return redirect(redireccion_por_rol(user))
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')

    return render(request, 'accounts/registro.html', {'form': form})


@login_required
def perfil_view(request):
    """Vista del perfil del usuario autenticado."""
    form = EditarUsuarioForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores.')

    return render(request, 'accounts/perfil.html', {'form': form})


@login_required
@solo_admin
def lista_usuarios_view(request):
    """Vista de administración de usuarios (solo admin)."""
    usuarios = Usuario.objects.all().order_by('rol', 'username')
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@solo_admin
def toggle_usuario_view(request, pk):
    """Activar o desactivar un usuario."""
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('accounts:lista_usuarios')
    usuario.activo = not usuario.activo
    usuario.save()
    estado = 'activado' if usuario.activo else 'desactivado'
    messages.success(request, f'Usuario {usuario.username} {estado} correctamente.')
    return redirect('accounts:lista_usuarios')
