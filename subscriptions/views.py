from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from billing.models import BillingStatement
from images.forms import UploadImage
from images.models import Image
from partner.models import get_partner_or_401
from patreonlink.forms import PatreonAPIForm
from .forms import *


def index(request):
    campaign_list = SubscriptionCampaign.objects.all()

    context = {
        'campaign_list': campaign_list,
    }
    return TemplateResponse(request, "subscription/index.html", context=context)


def view_campaign(request, partner_slug=None, campaign_slug=None):
    campaign = SubscriptionCampaign.objects.get(slug=campaign_slug)
    context = {
        'campaign': campaign,
    }
    return TemplateResponse(request, "subscription/view_sub.html", context=context)


def view_pack(request, pack_id, partner_slug=None, campaign_slug=None):
    pack = get_object_or_404(SubscriptionPack, id=pack_id)

    if request.user.is_authenticated:
        pack.check_pledges_to_populate_downloads(request.user)

    download_list = {}
    unpurchased = []
    for di in pack.contents.all():
        if di.user_already_owns(request.user):
            download_list[di] = di.root_downloadable.create_dict(user=request.user)
        else:
            unpurchased.append(di)
    if len(download_list) > 0:
        if not EmailAddress.objects.filter(
                user=request.user, verified=True
        ).exists():
            send_email_confirmation(request, request.user)
            return TemplateResponse(request, "account/verified_email_required.html")
    context = {
        'pack': pack,
        'download_list': download_list,
        'unpurchased': unpurchased,
        'purchased': True,  # Don't include any di rows to this view that aren't actually purchased
    }
    return TemplateResponse(request, "subscription/view_pack.html", context=context)


def view_pack_manage(request, campaign_id, pack_id, partner_slug):
    pack = get_object_or_404(SubscriptionPack, id=pack_id)
    partner = get_partner_or_401(request, partner_slug)

    download_list = {}
    for di in pack.contents.all():
        download_list[di] = di.root_downloadable.create_dict(user=request.user)

    emails = pack.qualifying_patreon_pledges.values_list('email').distinct()
    users = User.objects.filter(id__in=pack.qualifying_patreon_pledges.values_list('user').distinct())

    charges_summary = {}

    billing_statements = pack.billing_events.order_by('statement').values_list('statement',
                                                                               flat=True).distinct()
    for statement in BillingStatement.objects.filter(id__in=billing_statements):
        charges_summary[statement] = pack.billing_events.filter(statement=statement).prefetch_related("user")

    context = {
        'partner': partner,
        'pack': pack,
        'download_list': download_list,
        'purchased': True,  # Don't include any di rows to this view that aren't actually purchased
        'users': users,
        'emails': emails,
        'charges': charges_summary,

    }
    return TemplateResponse(request, "subscription/view_pack_manage.html", context=context)


def edit_patreon_api_view(request, partner_slug, campaign_id, discount_id=""):
    partner = get_partner_or_401(request, partner_slug)
    campaign = get_object_or_404(SubscriptionCampaign, id=campaign_id)
    next_url = reverse("manage_subscriptions", kwargs={'partner_slug': partner.slug})

    form = PatreonAPIForm(instance=campaign.patreon_campaign)

    if request.method == 'POST':
        form = PatreonAPIForm(request.POST, instance=campaign.patreon_campaign)
        if form.is_valid():
            print("Creating new pack")
            form.save()
            return HttpResponseRedirect(next_url)

    context = {
        'title': "Edit Patreon API Configuration",
        'partner': partner,
        'form': form
    }
    return TemplateResponse(request, "create_from_form.html", context=context)


def download_pack(request, pack_id):
    pack = get_object_or_404(SubscriptionPack, id=pack_id)
    download_list = []
    for di in pack.contents.all():
        if di.user_already_owns(request.user):
            download_list.append({'filename': di.product.slug + " " + datetime.datetime.utcnow().strftime("%Y%m%d%H%i"),
                                  'di_id': di.id,
                                  'downloadable_id': di.root_downloadable.id})
    data = {
        'pack': pack.name,
        'download_list': download_list,
    }
    return JsonResponse(data)


def manage_subscriptions(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug)
    context = {
        'partner': partner,
    }
    return TemplateResponse(request, "subscription/manage_subscriptions.html", context=context)


def edit_discount(request, partner_slug, campaign_id, discount_id=""):
    partner = get_partner_or_401(request, partner_slug)
    campaign = get_object_or_404(SubscriptionCampaign, id=campaign_id)
    next_url = reverse("manage_subscriptions", kwargs={'partner_slug': partner.slug})

    form = DiscountForm(partner=partner, campaign=campaign)

    if discount_id != "":
        discount = get_object_or_404(SubscriberDiscount, id=discount_id, campaign=campaign)
        if request.method == 'POST':
            print("Updating existing pack")
            form = DiscountForm(request.POST, partner=partner, campaign=campaign, instance=discount)
            if form.is_valid():
                form.save_to_patreon(campaign)
                return HttpResponseRedirect(next_url)
        else:
            form = DiscountForm(partner=partner, campaign=campaign, instance=discount)
    elif request.method == 'POST':
        form = DiscountForm(request.POST, partner=partner, campaign=campaign)
        if form.is_valid():
            print("Creating new pack")
            form.save_to_patreon(campaign)
            return HttpResponseRedirect(next_url)

    context = {
        'title': "Create or edit Discount",
        'partner': partner,
        'form': form
    }
    return TemplateResponse(request, "create_from_form.html", context=context)


def edit_tier(request, partner_slug, campaign_id, tier_id=""):
    partner = get_partner_or_401(request, partner_slug)
    campaign = get_object_or_404(SubscriptionCampaign, id=campaign_id)
    next_url = reverse("manage_subscriptions", kwargs={'partner_slug': partner.slug})

    if tier_id != "":
        tier = get_object_or_404(SubscriptionTier, id=tier_id, campaign=campaign)
        if request.method == 'POST':
            form = TierForm(request.POST, partner=partner, campaign=campaign, instance=tier)
            form.save_to_patreon(campaign)
            return HttpResponseRedirect(next_url)
        else:
            form = TierForm(partner=partner, campaign=campaign, instance=tier)
    elif request.method == 'POST':
        form = TierForm(request.POST, partner=partner, campaign=campaign)
        if form.is_valid():
            print("Creating new pack")
            form.save_to_patreon(campaign)
            return HttpResponseRedirect(next_url)
    else:
        form = TierForm(partner=partner, campaign=campaign)

    context = {
        'title': "Create or edit Discount",
        'partner': partner,
        'form': form
    }
    return TemplateResponse(request, "create_from_form.html", context=context)


def edit_pack(request, partner_slug, campaign_id, pack_id=""):
    partner = get_partner_or_401(request, partner_slug)
    campaign = get_object_or_404(SubscriptionCampaign, id=campaign_id)
    next_url = reverse("manage_subscriptions", kwargs={'partner_slug': partner.slug})
    print(next_url)
    print(partner.slug, campaign_id, pack_id)
    pack = None
    form = None
    if pack_id != "":
        pack = get_object_or_404(SubscriptionPack, id=pack_id, campaign=campaign)
        if request.method == 'POST':
            print("Updating existing pack")
            form = PackForm(request.POST, partner=partner, campaign=campaign, instance=pack)
            if form.is_valid():
                form.save_to_patreon(campaign)
                return HttpResponseRedirect(next_url)
        else:
            form = PackForm(partner=partner, campaign=campaign, instance=pack)
    elif request.method == 'POST':
        form = PackForm(request.POST, partner=partner, campaign=campaign)
        if form.is_valid():
            print("Creating new pack")
            form.save_to_patreon(campaign)
            return HttpResponseRedirect(next_url)
    else:
        form = PackForm(partner=partner, campaign=campaign)

    context = {
        'title': "Creating or editing pack",
        'partner': partner,
        'form': form
    }
    if pack_id:
        context['pack'] = pack
    return TemplateResponse(request, "subscription/edit_pack.html", context=context)


def delete_pack(request, partner_slug, campaign_id, pack_id, confirm):
    partner = get_partner_or_401(request, partner_slug)
    campaign = get_object_or_404(SubscriptionCampaign, id=campaign_id)
    pack = get_object_or_404(SubscriptionPack, id=pack_id, campaign=campaign)
    next_url = reverse("manage_subscriptions", kwargs={'partner_slug': partner.slug})

    if int(confirm) == 1:
        pack.delete()
        return HttpResponseRedirect(next_url)
    else:

        context = {
            'item_name': pack.name,
            'confirm_url': reverse("delete_pack", kwargs={'partner_slug': partner.slug,
                                                          'campaign_id': campaign_id,
                                                          'pack_id': pack_id,
                                                          'confirm': 1}),
            'back_url': next_url,
        }
        return TemplateResponse(request, "confirm_delete.html", context=context)


def delete_discount(request, partner_slug, campaign_id, discount_id, confirm):
    partner = get_partner_or_401(request, partner_slug)
    campaign = get_object_or_404(SubscriptionCampaign, id=campaign_id)
    discount = get_object_or_404(SubscriberDiscount, id=discount_id, campaign=campaign)
    next_url = reverse("manage_subscriptions", kwargs={'partner_slug': partner.slug})

    if int(confirm) == 1:
        discount.delete()
        return HttpResponseRedirect(next_url)
    else:

        context = {
            'item_name': discount,
            'confirm_url': reverse("delete_discount", kwargs={'partner_slug': partner.slug,
                                                              'campaign_id': campaign_id,
                                                              'discount_id': discount_id,
                                                              'confirm': 1}),
            'back_url': next_url,
        }
        return TemplateResponse(request, "confirm_delete.html", context=context)


# def delete_tier(request, partner_slug, campaign_id, tier_id, confirm):
#     partner = get_partner_or_404(request, partner_slug)
#     campaign = get_object_or_404(SubscriptionCampaign, id=campaign_id)
#     tier = get_object_or_404(SubscriberDiscount, id=tier_id, campaign=campaign)
#     next_url = reverse("manage_subscriptions", kwargs={'partner_slug': partner.slug})
#
#     if int(confirm) == 1:
#         tier.delete()
#         return HttpResponseRedirect(next_url)
#     else:
#
#         context = {
#             'item_name': tier,
#             'confirm_url': reverse("delete_tier", kwargs={'partner_slug': partner.slug,
#                                                           'campaign_id': campaign_id,
#                                                           'tier_id': tier_id,
#                                                           'confirm': 1}),
#             'back_url': next_url,
#         }
#         return TemplateResponse(request, "confirm_delete.html", context=context)


def upload_pack_image(request, partner_slug, campaign_id, pack_id):
    partner = get_partner_or_401(request, partner_slug)
    pack = get_object_or_404(SubscriptionPack, id=pack_id)
    print(request.method)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UploadImage(request.POST, request.FILES)
        print(form)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            image = form.save(commit=False)
            image.partner = partner
            image.save()
            pack.primary_image = image
            pack.save()
            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse("edit_pack", kwargs={'partner_slug': partner.slug,
                                             'pack_id': pack.id,
                                             'campaign_id': pack.campaign.id}
                        ))

        else:
            print("form is not valid")
    context = {
        'form': UploadImage(),
        'partner': partner
    }
    return TemplateResponse(request, "create_from_form.html", context=context)


def remove_image(request, partner_slug, campaign_id, pack_id, image_id):
    partner = get_partner_or_401(request, partner_slug)
    pack = get_object_or_404(SubscriptionPack, id=pack_id)
    try:
        image = get_object_or_404(Image, id=image_id)
        if pack.primary_image == image:
            pack.primary_image = None
            pack.save()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(
        reverse("edit_pack", kwargs={'partner_slug': partner.slug,
                                     'pack_id': pack.id,
                                     'campaign_id': pack.campaign.id}
                ))


def grant_manual_access(request, partner_slug, customer_id):
    partner = get_partner_or_401(request, partner_slug)
    user = get_object_or_404(User, id=customer_id)

    if request.method == "POST":
        form = GrantManualAccessForm(request.POST, partner=partner)
        form.save(user)

    return HttpResponseRedirect(
        reverse("partner_customer_details", kwargs={'partner_slug': partner.slug,
                                                    'user_id': customer_id})
    )


def revoke_manual_access(request, partner_slug, customer_id):
    partner = get_partner_or_401(request, partner_slug)
    user = get_object_or_404(User, id=customer_id)

    if request.method == "POST":
        form = RevokeManualAccessForm(request.POST, partner=partner)
        form.save(user)

    return HttpResponseRedirect(
        reverse("partner_customer_details", kwargs={'partner_slug': partner.slug,
                                                    'user_id': customer_id})
    )


@login_required
def onboarding(request, campaign_slug):
    campaign = get_object_or_404(SubscriptionCampaign, slug=campaign_slug)
    try:
        current_subscription = SubscriberList.objects.get(user=request.user, tier__in=campaign.tiers.filter(
            allow_on_site_subscriptions=True))
    except Exception:
        current_subscription = None
    form = OnboardingForm(campaign=campaign, user=request.user, instance=current_subscription)
    if request.method == "POST":
        form = OnboardingForm(request.POST, campaign=campaign, user=request.user, instance=current_subscription)
        print(request.POST)
        if form.is_valid():
            try:
                UserDefaultAddress.objects.create(address=form.cleaned_data['address'], user=request.user)
            except Exception as e:
                print(e)
            list_entry = form.save(commit=False)
            if list_entry.tier.limit \
                    and SubscriberList.objects.filter(tier=list_entry.tier).count() < list_entry.tier.limit:
                list_entry.user = request.user
                if form.cleaned_data['start_now'] is False:
                    x = datetime.date.today()
                    next_month_start = None
                    try:
                        next_month_start = x.replace(month=x.month + 1, day=1)
                    except ValueError:
                        if x.month == 12:
                            next_month_start = x.replace(year=x.year + 1, month=1, day=1)
                    list_entry.start_date = next_month_start
                    list_entry.save()
                else:
                    list_entry.save()

    cards = stripe.PaymentMethod.list(
        customer=request.user.stripe_id.id,
        type="card",
    )
    intent = stripe.SetupIntent.create(
        customer=request.user.stripe_id.id,
    )
    context = {
        'current_subscription': current_subscription,
        'campaign': campaign,
        'cards': cards,
        'intent': intent,
        'publishableAPIKey': settings.STRIPE_PUBLIC_KEY,
        'form': form,
    }
    return TemplateResponse(request, 'subscription/onboarding.html', context)
