from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Paciente, HistoriaClinica
from .forms import PacienteForm, HistoriaClinicaForm, BuscarPacienteForm
from .utils import exportar_pacientes_excel, exportar_historia_pdf


def requiere_admin_o_medico(request):
    if request.user.is_superuser or getattr(request.user, 'rol', None) in ['admin', 'medico']:
        return True
    messages.error(request, 'No tienes permisos para acceder a gestion de pacientes.')
    return False


# ─────────────────────────────────────────────
#  CRUD PACIENTES
# ─────────────────────────────────────────────

@login_required
def lista_pacientes(request):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Lista de pacientes con búsqueda, filtros y paginación."""
    form = BuscarPacienteForm(request.GET or None)
    pacientes = Paciente.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get('q')
        activo = form.cleaned_data.get('activo')

        if q:
            pacientes = pacientes.filter(
                Q(nombre__icontains=q) |
                Q(apellido__icontains=q) |
                Q(dni__icontains=q) |
                Q(email__icontains=q)
            )
        if activo == '1':
            pacientes = pacientes.filter(activo=True)
        elif activo == '0':
            pacientes = pacientes.filter(activo=False)

    total = pacientes.count()

    # Paginación: 10 pacientes por página
    paginator = Paginator(pacientes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pacientes/lista.html', {
        'pacientes': page_obj,
        'page_obj': page_obj,
        'form': form,
        'total': total,
    })


@login_required
def detalle_paciente(request, pk):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Detalle de un paciente con su historia clínica."""
    paciente = get_object_or_404(Paciente, pk=pk)
    historias = paciente.historias.all()
    return render(request, 'pacientes/detalle.html', {
        'paciente': paciente,
        'historias': historias,
    })


@login_required
def crear_paciente(request):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Crear un nuevo paciente."""
    form = PacienteForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            paciente = form.save()
            messages.success(request, f'Paciente {paciente.nombre_completo()} creado correctamente.')
            return redirect('pacientes:detalle', pk=paciente.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')

    return render(request, 'pacientes/form.html', {
        'form': form,
        'titulo': 'Nuevo Paciente',
        'accion': 'Crear',
    })


@login_required
def editar_paciente(request, pk):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Editar un paciente existente."""
    paciente = get_object_or_404(Paciente, pk=pk)
    form = PacienteForm(request.POST or None, instance=paciente)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Paciente {paciente.nombre_completo()} actualizado correctamente.')
            return redirect('pacientes:detalle', pk=paciente.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')

    return render(request, 'pacientes/form.html', {
        'form': form,
        'titulo': f'Editar Paciente: {paciente.nombre_completo()}',
        'accion': 'Guardar cambios',
        'paciente': paciente,
    })


@login_required
def eliminar_paciente(request, pk):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Eliminar un paciente (requiere confirmación POST)."""
    paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        nombre = paciente.nombre_completo()
        paciente.delete()
        messages.success(request, f'Paciente {nombre} eliminado correctamente.')
        return redirect('pacientes:lista')

    return render(request, 'pacientes/confirmar_eliminar.html', {'paciente': paciente})


# ─────────────────────────────────────────────
#  HISTORIA CLÍNICA
# ─────────────────────────────────────────────

@login_required
def agregar_historia(request, pk):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Agregar una entrada a la historia clínica de un paciente."""
    paciente = get_object_or_404(Paciente, pk=pk)
    form = HistoriaClinicaForm(request.POST or None, initial={'fecha': timezone.now().date()})

    if request.method == 'POST':
        if form.is_valid():
            historia = form.save(commit=False)
            historia.paciente = paciente
            historia.save()
            messages.success(request, 'Registro clínico agregado correctamente.')
            return redirect('pacientes:detalle', pk=paciente.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')

    return render(request, 'pacientes/historia_form.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Nueva Entrada Clínica',
    })


@login_required
def editar_historia(request, pk, historia_pk):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Editar una entrada de historia clínica."""
    paciente = get_object_or_404(Paciente, pk=pk)
    historia = get_object_or_404(HistoriaClinica, pk=historia_pk, paciente=paciente)
    form = HistoriaClinicaForm(request.POST or None, instance=historia)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro clínico actualizado correctamente.')
            return redirect('pacientes:detalle', pk=paciente.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')

    return render(request, 'pacientes/historia_form.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Editar Entrada Clínica',
    })


@login_required
def eliminar_historia(request, pk, historia_pk):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Eliminar una entrada de historia clínica."""
    paciente = get_object_or_404(Paciente, pk=pk)
    historia = get_object_or_404(HistoriaClinica, pk=historia_pk, paciente=paciente)

    if request.method == 'POST':
        historia.delete()
        messages.success(request, 'Registro clínico eliminado correctamente.')
        return redirect('pacientes:detalle', pk=paciente.pk)

    return render(request, 'pacientes/confirmar_eliminar_historia.html', {
        'paciente': paciente,
        'historia': historia,
    })


# ─────────────────────────────────────────────
#  EXPORTACIONES
# ─────────────────────────────────────────────

@login_required
def exportar_excel(request):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Exportar lista de pacientes a Excel."""
    form = BuscarPacienteForm(request.GET or None)
    pacientes = Paciente.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get('q')
        activo = form.cleaned_data.get('activo')
        if q:
            pacientes = pacientes.filter(
                Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(dni__icontains=q)
            )
        if activo == '1':
            pacientes = pacientes.filter(activo=True)
        elif activo == '0':
            pacientes = pacientes.filter(activo=False)

    try:
        output = exportar_pacientes_excel(pacientes)
    except ImportError as exc:
        messages.error(request, f'No se pudo generar el Excel: {exc}')
        return redirect('pacientes:lista')

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="pacientes.xlsx"'
    return response


@login_required
def exportar_pdf(request, pk):
    if not requiere_admin_o_medico(request):
        return redirect('medicos:cita_lista')

    """Exportar historia clínica de un paciente a PDF."""
    paciente = get_object_or_404(Paciente, pk=pk)
    historias = paciente.historias.all()

    pdf_bytes = exportar_historia_pdf(paciente, historias)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="historia_{paciente.dni}.pdf"'
    return response
