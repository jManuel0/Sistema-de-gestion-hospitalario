from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from pacientes.models import Paciente
from .forms import BuscarCitaForm, BuscarMedicoForm, CitaForm, HorarioForm, MedicoForm, PacienteCitaForm
from .models import Cita, Horario, Medico
from .utils import enviar_confirmacion_cita


def errores_formulario_legibles(form):
    errores = []
    for campo, lista_errores in form.errors.items():
        etiqueta = ''
        if campo != '__all__' and campo in form.fields:
            etiqueta = f'{form.fields[campo].label}: '
        for error in lista_errores:
            errores.append(f'{etiqueta}{error}')
    return errores


def obtener_o_crear_paciente_para_usuario(user):
    if hasattr(user, 'paciente_perfil'):
        return user.paciente_perfil
    return None


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_superuser or getattr(user, 'rol', None) == 'admin')

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para realizar esta accion.')
        return redirect('medicos:cita_lista')


class AdminOrMedicoRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser or getattr(user, 'rol', None) in ['admin', 'medico']
        )

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta seccion.')
        return redirect('medicos:cita_lista')


class CitaQuerysetMixin:
    def get_queryset(self):
        qs = Cita.objects.select_related('paciente', 'medico', 'medico__usuario')
        user = self.request.user

        if user.is_superuser or getattr(user, 'rol', None) == 'admin':
            return qs
        if getattr(user, 'rol', None) == 'medico' and hasattr(user, 'medico_perfil'):
            return qs.filter(medico=user.medico_perfil)
        if getattr(user, 'rol', None) == 'paciente':
            paciente = obtener_o_crear_paciente_para_usuario(user)
            if not paciente:
                return qs.none()
            return qs.filter(paciente=paciente)
        return qs.none()


class MedicoListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Medico
    template_name = 'medicos/medico_list.html'
    context_object_name = 'medicos'
    paginate_by = 10

    def get_queryset(self):
        qs = Medico.objects.select_related('usuario')
        self.form = BuscarMedicoForm(self.request.GET or None)
        if self.form.is_valid():
            q = self.form.cleaned_data.get('q')
            activo = self.form.cleaned_data.get('activo')
            if q:
                qs = qs.filter(
                    Q(usuario__first_name__icontains=q) |
                    Q(usuario__last_name__icontains=q) |
                    Q(usuario__username__icontains=q) |
                    Q(especialidad__icontains=q) |
                    Q(numero_licencia__icontains=q)
                )
            if activo == '1':
                qs = qs.filter(activo=True)
            elif activo == '0':
                qs = qs.filter(activo=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['total'] = self.get_queryset().count()
        return context


class MedicoDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Medico
    template_name = 'medicos/medico_detail.html'
    context_object_name = 'medico'

    def get_queryset(self):
        return Medico.objects.select_related('usuario').prefetch_related('horarios')


class MedicoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Medico
    form_class = MedicoForm
    template_name = 'medicos/medico_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Medico creado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores del formulario.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('medicos:medico_detalle', kwargs={'pk': self.object.pk})


class MedicoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Medico
    form_class = MedicoForm
    template_name = 'medicos/medico_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Medico actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores del formulario.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('medicos:medico_detalle', kwargs={'pk': self.object.pk})


class MedicoDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Medico
    template_name = 'medicos/medico_confirm_delete.html'
    success_url = reverse_lazy('medicos:medico_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Medico eliminado correctamente.')
        return super().form_valid(form)


class HorarioListView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, ListView):
    model = Horario
    template_name = 'medicos/horario_list.html'
    context_object_name = 'horarios'
    paginate_by = 15

    def get_queryset(self):
        qs = Horario.objects.select_related('medico', 'medico__usuario')
        user = self.request.user
        if getattr(user, 'rol', None) == 'medico' and hasattr(user, 'medico_perfil'):
            qs = qs.filter(medico=user.medico_perfil)
        elif getattr(user, 'rol', None) == 'paciente':
            qs = qs.filter(activo=True, medico__activo=True)
        return qs


class HorarioCreateView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, CreateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'medicos/horario_form.html'
    success_url = reverse_lazy('medicos:horario_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if getattr(self.request.user, 'rol', None) == 'medico':
            form.instance.medico = self.request.user.medico_perfil
        messages.success(self.request, 'Horario creado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in errores_formulario_legibles(form):
            messages.error(self.request, error)
        return super().form_invalid(form)


class HorarioUpdateView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, UpdateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'medicos/horario_form.html'
    success_url = reverse_lazy('medicos:horario_lista')

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, 'rol', None) == 'medico':
            qs = qs.filter(medico=self.request.user.medico_perfil)
        return qs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if getattr(self.request.user, 'rol', None) == 'medico':
            form.instance.medico = self.request.user.medico_perfil
        messages.success(self.request, 'Horario actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in errores_formulario_legibles(form):
            messages.error(self.request, error)
        return super().form_invalid(form)


class HorarioDeleteView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, DeleteView):
    model = Horario
    template_name = 'medicos/medico_confirm_delete.html'
    success_url = reverse_lazy('medicos:horario_lista')

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, 'rol', None) == 'medico':
            qs = qs.filter(medico=self.request.user.medico_perfil)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objeto_tipo'] = 'horario'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Horario eliminado correctamente.')
        return super().form_valid(form)


class CitaListView(LoginRequiredMixin, CitaQuerysetMixin, ListView):
    model = Cita
    template_name = 'medicos/cita_list.html'
    context_object_name = 'citas'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, 'rol', None) == 'paciente':
            return qs.filter(fecha__gte=date.today()).order_by('fecha', 'hora')

        self.form = BuscarCitaForm(self.request.GET or None, user=self.request.user)
        if self.form.is_valid():
            q = self.form.cleaned_data.get('q')
            fecha = self.form.cleaned_data.get('fecha')
            medico = self.form.cleaned_data.get('medico')
            estado = self.form.cleaned_data.get('estado')
            if q:
                qs = qs.filter(
                    Q(paciente__nombre__icontains=q) |
                    Q(paciente__apellido__icontains=q) |
                    Q(paciente__dni__icontains=q) |
                    Q(medico__usuario__first_name__icontains=q) |
                    Q(medico__usuario__last_name__icontains=q) |
                    Q(motivo__icontains=q)
                )
            if fecha:
                qs = qs.filter(fecha=fecha)
            if medico:
                qs = qs.filter(medico=medico)
            if estado:
                qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = getattr(self, 'form', BuscarCitaForm(user=self.request.user))
        context['total'] = self.get_queryset().count()
        return context


class CitaDetailView(LoginRequiredMixin, CitaQuerysetMixin, DetailView):
    model = Cita
    template_name = 'medicos/cita_detail.html'
    context_object_name = 'cita'


class CitaCreateView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'medicos/cita_form.html'

    def dispatch(self, request, *args, **kwargs):
        if getattr(request.user, 'rol', None) == 'medico' and not hasattr(request.user, 'medico_perfil'):
            messages.error(request, 'Tu usuario medico no tiene perfil de medico asociado.')
            return redirect('medicos:cita_lista')
        if getattr(request.user, 'rol', None) == 'paciente':
            if not obtener_o_crear_paciente_para_usuario(request.user):
                messages.error(request, 'Tu cuenta no tiene un perfil de paciente con DNI / cedula. Contacta al administrador.')
                return redirect('medicos:cita_lista')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_form_class(self):
        if getattr(self.request.user, 'rol', None) == 'paciente':
            return PacienteCitaForm
        return CitaForm

    def form_valid(self, form):
        self.object = form.save()
        enviar_confirmacion_cita(self.object)
        if getattr(self.request.user, 'rol', None) == 'paciente':
            messages.success(self.request, 'Cita agendada correctamente.')
        else:
            messages.success(self.request, 'Cita creada correctamente. Se envio la confirmacion por correo si el paciente tiene email.')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        for error in errores_formulario_legibles(form):
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        if getattr(self.request.user, 'rol', None) == 'paciente':
            return reverse_lazy('medicos:cita_lista')
        return reverse_lazy('medicos:cita_detalle', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['horarios_medicos'] = (
            Horario.objects
            .filter(medico__activo=True, activo=True)
            .select_related('medico', 'medico__usuario')
            .order_by('medico__usuario__last_name', 'medico__usuario__first_name', 'dia_semana', 'hora_inicio')
        )
        return context


class CitaUpdateView(LoginRequiredMixin, CitaQuerysetMixin, UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = 'medicos/cita_form.html'

    def dispatch(self, request, *args, **kwargs):
        if getattr(request.user, 'rol', None) == 'paciente':
            messages.error(request, 'No tienes permisos para editar citas.')
            return redirect('medicos:cita_lista')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        if getattr(user, 'rol', None) == 'medico' and form.instance.medico != user.medico_perfil:
            raise PermissionDenied
        if getattr(user, 'rol', None) == 'paciente':
            if form.instance.paciente != user.paciente_perfil:
                raise PermissionDenied
        self.object = form.save()
        messages.success(self.request, 'Cita actualizada correctamente.')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        for error in errores_formulario_legibles(form):
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('medicos:cita_detalle', kwargs={'pk': self.object.pk})


class CitaDeleteView(LoginRequiredMixin, CitaQuerysetMixin, DeleteView):
    model = Cita
    template_name = 'medicos/cita_confirm_delete.html'
    success_url = reverse_lazy('medicos:cita_lista')

    def dispatch(self, request, *args, **kwargs):
        if getattr(request.user, 'rol', None) == 'paciente':
            messages.error(request, 'No tienes permisos para eliminar citas.')
            return redirect('medicos:cita_lista')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Cita eliminada correctamente.')
        return super().form_valid(form)
