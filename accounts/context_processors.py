def rol_usuario(request):
    """
    Inyecta helpers de rol en todos los templates.
    Uso en template: {% if es_admin %} ... {% endif %}
    """
    if request.user.is_authenticated:
        return {
            'es_admin': request.user.rol == 'admin' or request.user.is_superuser,
            'es_medico': request.user.rol == 'medico',
            'es_paciente': request.user.rol == 'paciente',
        }
    return {
        'es_admin': False,
        'es_medico': False,
        'es_paciente': False,
    }
