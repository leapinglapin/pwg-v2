from django.shortcuts import render

from checkout.models import Cart
# Create your views here.
from partner.models import get_partner_or_401


def sales_overview(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    carts = Cart.submitted.exclude(status__in=['Cancelled', 'Submitted'])
    context = {
        'partner': partner,
        'carts': carts,
    }
    return render(request, "partner_sales_overview.html", context)
