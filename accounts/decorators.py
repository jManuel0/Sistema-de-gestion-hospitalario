from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def rol_requerido(*roles):
    """
    Decorador que restringe el acceso a vistas según el rol del usuario.
    Uso: @rol_requerido('admin', 'medico')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.rol not in roles and not request.user.is_superuser:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('pacientes:lista')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def solo_admin(view_func):
    """Decorador que permite acceso solo a administradores."""
    return rol_requerido('admin')(view_func)


def admin_o_medico(view_func):
    """Decorador que permite acceso a administradores y médicos."""
    return rol_requerido('admin', 'medico')(view_func)
