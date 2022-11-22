from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DeleteView

from inventory_report.models import InventoryReport, InventoryReportLocation, InventoryReportLine
from partner.models import get_partner_or_401


@login_required
def index(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug)
    context = {
        'partner': partner,
        'reports': InventoryReport.objects.filter(partner=partner),
    }
    return render(request, "inventory_report/index.html", context)


@login_required
def report_details(request, partner_slug, report_id):
    partner = get_partner_or_401(request, partner_slug)
    report = InventoryReport.objects.get(id=report_id, partner=partner)
    context = {
        'partner': partner,
        'report': report,
        'locations': InventoryReportLocation.objects.filter(partner=partner),
        'lines': report.report_lines.all().order_by('-timestamp')
    }
    return render(request, "inventory_report/report.html", context)


@login_required
def report_location(request, partner_slug, report_id, location_id):
    partner = get_partner_or_401(request, partner_slug)
    report = InventoryReport.objects.get(id=report_id, partner=partner)
    location = InventoryReportLocation.objects.get(id=location_id, partner=partner)
    context = {
        'partner': partner,
        'location': location,
        'report': report,
        'lines': report.report_lines.filter(location=location).order_by('-timestamp')
    }
    return render(request, "inventory_report/report.html", context)


@login_required
def add(request, partner_slug, report_id, location_id=None, barcode=None):
    partner = get_partner_or_401(request, partner_slug)
    report = InventoryReport.objects.get(id=report_id, partner=partner)
    location = None
    if location_id:
        location = InventoryReportLocation.objects.get(id=location_id)
    if barcode:
        InventoryReportLine.objects.create(report=report, location=location, barcode=barcode)

    return HttpResponse()

