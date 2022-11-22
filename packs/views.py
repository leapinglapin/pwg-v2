from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse
from django.urls import reverse

from packs.forms import AddDigitalPackForm
from packs.models import DigitalPack
from partner.models import get_partner_or_401


def manage_packs(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug)
    packs = DigitalPack.objects.filter(partner=partner)
    context = {
        'partner': partner,
        'packs': packs,
    }
    return TemplateResponse(request, "packs/manage_packs.html", context=context)


def manage_pack(request, partner_slug, pack_id):
    pack = DigitalPack.objects.get(id=pack_id)
    partner = get_partner_or_401(request, partner_slug, [pack])

    context = {
        'partner': partner,
        'pack': pack,
    }
    return TemplateResponse(request, "packs/manage_pack.html", context=context)


def create_edit_pack(request, partner_slug, pack_id=None):
    partner = get_partner_or_401(request, partner_slug)
    pack = None
    if pack_id:
        pack = DigitalPack.objects.get(id=pack_id)
    form = AddDigitalPackForm(instance=pack, partner=partner)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddDigitalPackForm(request.POST, instance=pack, partner=partner)
        # check whether it's valid:
        if form.is_valid():
            pack_product = form.save(commit=False)
            pack_product.partner = partner
            pack_product.save()
            form.save_m2m()
            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse("manage_product", kwargs={'partner_slug': partner.slug, 'product_slug': pack_product.slug}))
    context = {
        'form': form,
        'partner': partner,
    }
    return TemplateResponse(request, "create_from_form.html", context=context)
