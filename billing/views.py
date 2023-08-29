import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from billing.forms import StaffLogBillingEventForm, StaffLogOtherBillingEventForm
from billing.models import BillingStatement, BillingEvent
# Create your views here.
from partner.models import get_partner_or_401


def partner_billing_statements(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    statements = partner.billingstatement_set.filter(events__isnull=False).distinct().order_by("-statement_start")
    context = {
        'partner': partner,
        'statements': statements,
        'balance': partner.partnerbalance.get_calculated_balance(),
    }
    return render(request, "partner/billing/partner_billing_statements.html", context)


def partner_billing_statement_details(request, partner_slug, statement_id):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    statement = get_object_or_404(BillingStatement, id=statement_id)
    events = statement.events.select_related('user').prefetch_related(
        'linked_to_packs__campaign')
    context = {
        'partner': partner,
        'statement': statement,
        'summary': statement.get_summary(),
        'non_ic_events': events.exclude(type=BillingEvent.INTEGRATION_CHARGE),
        'ic_events': events.filter(type=BillingEvent.INTEGRATION_CHARGE),
        'pack_summary': statement.integration_charges_by_pack(),
    }
    return render(request, "partner/billing/statement_details.html", context)


def partner_billing_not_on_statement(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    events = BillingEvent.objects.filter(partner=partner, statement__isnull=True).select_related('user')
    total = events.aggregate(Sum('final_total'))['final_total__sum']
    context = {
        'partner': partner,
        'total': total,
        'non_ic_events': events.exclude(type=BillingEvent.INTEGRATION_CHARGE),
        'ic_events': events.filter(type=BillingEvent.INTEGRATION_CHARGE),
        'balance': partner.partnerbalance.get_calculated_balance(),

    }
    return render(request, "partner/billing/statement_details.html", context)


@staff_member_required
def log_payment(request, partner_slug, next_url=None):
    form = StaffLogBillingEventForm()
    partner = get_partner_or_401(request, partner_slug=partner_slug)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StaffLogBillingEventForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            print(form.cleaned_data)
            amount = form.cleaned_data['amount']
            fees = form.cleaned_data['payment_processor_fees']
            BillingEvent.objects.create(
                partner=partner,
                type=BillingEvent.PAYMENT,
                timestamp=datetime.datetime.now(),
                subtotal=amount,
                processing_fee=fees,
                final_total=amount - fees,
                comments=form.cleaned_data['comments'],
            )
            # redirect to a new URL:
            if next_url is None:
                next_url = reverse('billing_not_on_statement', kwargs={'partner_slug': partner.slug})
            return HttpResponseRedirect(next_url)

    context = {
        'form': form,
        'title': "Log payment from {}".format(partner.name),
        'balance': partner.partnerbalance.get_calculated_balance(),

    }
    return TemplateResponse(request, "partner/billing/log_billing_event_form.html", context=context)


@staff_member_required
def log_payout(request, partner_slug, next_url=None):
    form = StaffLogBillingEventForm()
    partner = get_partner_or_401(request, partner_slug=partner_slug)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StaffLogBillingEventForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            print(form.cleaned_data)
            amount = form.cleaned_data['amount']
            fees = form.cleaned_data['payment_processor_fees']
            BillingEvent.objects.create(
                partner=partner,
                type=BillingEvent.PAYOUT,
                timestamp=datetime.datetime.now(),
                subtotal=-amount,
                processing_fee=fees,
                final_total=-amount - fees,
                comments=form.cleaned_data['comments'],
            )
            # redirect to a new URL:
            if next_url is None:
                next_url = reverse('billing_not_on_statement', kwargs={'partner_slug': partner.slug})
            return HttpResponseRedirect(next_url)

    context = {
        'form': form,
        'title': "Log payout to {}".format(partner.name),
        'balance': partner.partnerbalance.get_calculated_balance(),
    }
    return TemplateResponse(request, "partner/billing/log_billing_event_form.html", context=context)


@staff_member_required
def log_other(request, partner_slug, next_url=None):
    form = StaffLogOtherBillingEventForm(initial={'type': BillingEvent.OTHER})
    partner = get_partner_or_401(request, partner_slug=partner_slug)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StaffLogOtherBillingEventForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            print(form.cleaned_data)
            amount = form.cleaned_data['amount']
            fees = form.cleaned_data['payment_processor_fees']
            BillingEvent.objects.create(
                partner=partner,
                type=form.cleaned_data['type'],
                timestamp=datetime.datetime.now(),
                subtotal=amount,
                processing_fee=fees,
                final_total=amount - fees,
                comments=form.cleaned_data['comments'],
            )
            # redirect to a new URL:
            if next_url is None:
                next_url = reverse('billing_not_on_statement', kwargs={'partner_slug': partner.slug})
            return HttpResponseRedirect(next_url)

    context = {
        'form': form,
        'title': "Log payout to {}".format(partner.name),
        'balance': partner.partnerbalance.get_calculated_balance(),
    }
    return TemplateResponse(request, "partner/billing/log_billing_event_form.html", context=context)
