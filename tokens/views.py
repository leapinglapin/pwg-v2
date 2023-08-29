from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from partner.models import get_partner_or_401
from shop.models import Item, Product
from tokens.forms import TokenCostForm, TokenForm
from tokens.models import Token, TokenCost, TokenBalance


@login_required
def manage_tokens(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug)
    context = {'partner': partner}
    return TemplateResponse(request, "tokens/partner_tokens.html", context=context)


@login_required
def user_view_token_balance(request):
    balances = TokenBalance.objects.get(user=request.user)
    context = {'balances': balances}

    return TemplateResponse(request, "tokens/user_balances.html", context=context)


@login_required()
def edit_token(request, partner_slug, token_id=""):
    partner = get_partner_or_401(request, partner_slug)

    token = None
    if token_id:
        token = get_object_or_404(Token, id=token_id)
        partner = get_partner_or_401(request, partner_slug, objects=[token])

    form = TokenForm(instance=token)
    next_url = reverse("manage_tokens", kwargs={'partner_slug': partner.slug})
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TokenForm(request.POST, instance=token)
        # check whether it's valid:
        if form.is_valid():
            token = form.save(commit=False)
            token.partner = partner
            token.save()
            return HttpResponseRedirect(next_url)

    context = {"form": form, "edit": True, 'partner': partner}

    return TemplateResponse(request, "create_from_form.html", context=context)


@login_required
def set_item_token_cost(request, partner_slug, product_slug, item_id, token_id=""):
    item = get_object_or_404(Item, id=item_id)
    partner = get_partner_or_401(request, partner_slug, objects=[item])
    token = get_object_or_404(Token, id=token_id)

    token = None
    tokenCost = None
    if token_id:
        tc_queryset = TokenCost.objects.filter(token=token, item=item)
        if tc_queryset.exists():
            tokenCost = tc_queryset.get()
    form = TokenCostForm(instance=tokenCost)
    next_url = reverse("manage_product", kwargs={'partner_slug': partner.slug,
                                                 'product_slug': product_slug})
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TokenCostForm(request.POST, instance=tokenCost)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(next_url)

    context = {"item": item, "form": form, "edit": True, 'partner': partner}

    return TemplateResponse(request, "create_from_form.html", context=context)


def delete_item_token_cost(request, partner_slug, product_slug, item_id, token_id, confirm=None):
    product = get_object_or_404(Product, slug=product_slug)
    item = get_object_or_404(Item, id=item_id)
    partner = get_partner_or_401(request, partner_slug, objects=[item])

    token = get_object_or_404(Token, id=token_id)

    next_url = reverse("manage_product", kwargs={'partner_slug': partner.slug,
                                                 'product_slug': product_slug})

    if int(confirm) == 1:
        tc_queryset = TokenCost.objects.filter(token=token, item=item)
        if tc_queryset.exists():
            tc_queryset.get().delete()
        return HttpResponseRedirect(next_url)
    else:

        context = {
            'item_name': "{}'s cost in {}".format(item.product.name, token.name),
            'confirm_url': reverse('delete_token_cost', kwargs={
                'partner_slug': partner.slug,
                'product_slug': product_slug,
                'item_id': item_id,
                'token_id': token_id,
                'confirm': 1,
            }),
            'back_url': next_url,
        }
        return TemplateResponse(request, "confirm_delete.html", context=context)
