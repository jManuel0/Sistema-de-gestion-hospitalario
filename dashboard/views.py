from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from accounts.decorators import admin_o_medico
from .reports import build_statistics_excel, build_statistics_pdf
from .services import get_dashboard_statistics, parse_dashboard_filters


@login_required
@admin_o_medico
def dashboard_home(request):
    filters = parse_dashboard_filters(request.GET)
    statistics = get_dashboard_statistics(filters)

    return render(request, 'dashboard/home.html', {
        'filters': filters,
        'resumen': statistics['resumen'],
        'charts': statistics['charts'],
    })


@login_required
@admin_o_medico
def export_statistics_excel(request):
    filters = parse_dashboard_filters(request.GET)
    statistics = get_dashboard_statistics(filters)
    output = build_statistics_excel(filters, statistics)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="dashboard_estadisticas.xlsx"'
    return response


@login_required
@admin_o_medico
def export_statistics_pdf(request):
    filters = parse_dashboard_filters(request.GET)
    statistics = get_dashboard_statistics(filters)
    output = build_statistics_pdf(filters, statistics)

    response = HttpResponse(output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dashboard_estadisticas.pdf"'
    return response
