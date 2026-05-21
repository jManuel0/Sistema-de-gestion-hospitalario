from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from medicos.models import Cita, Medico
from pacientes.models import Paciente
from .services import get_dashboard_statistics, parse_dashboard_filters


class DashboardTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin',
            password='test-pass-123',
            rol='admin',
        )
        medico_user = User.objects.create_user(
            username='medico',
            password='test-pass-123',
            rol='medico',
            first_name='Ana',
            last_name='Ruiz',
        )
        self.medico = medico_user.medico_perfil
        self.medico.especialidad = Medico.ESPECIALIDAD_CARDIOLOGIA
        self.medico.telefono = '3001234567'
        self.medico.numero_licencia = 'LIC-001'
        self.medico.save()
        self.paciente = Paciente.objects.create(
            dni='123',
            nombre='Laura',
            apellido='Perez',
            fecha_nacimiento=date(1990, 1, 1),
            genero='F',
            telefono='3000000000',
            email='laura@example.com',
        )
        Cita.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            fecha=date.today(),
            hora=time(9, 0),
            motivo='Control',
            estado=Cita.ESTADO_CONFIRMADA,
        )

    def test_dashboard_redirects_anonymous_users_and_builds_statistics(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

        filters = parse_dashboard_filters({'periodo': 'hoy'})
        statistics = get_dashboard_statistics(filters)
        self.assertEqual(statistics['resumen']['total_pacientes'], 1)
        self.assertEqual(statistics['resumen']['total_citas'], 1)

    def test_dashboard_exports(self):
        self.client.login(username='admin', password='test-pass-123')

        excel_response = self.client.get(reverse('dashboard:export_excel'))
        self.assertEqual(excel_response.status_code, 200)
        self.assertEqual(
            excel_response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        pdf_response = self.client.get(reverse('dashboard:export_pdf'))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
