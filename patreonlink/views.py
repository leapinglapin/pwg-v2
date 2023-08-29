import datetime

from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse

from partner.models import get_partner_or_401

from .models import *


def raw_data(request, member_id, partner_slug=None):
    member = None
    if partner_slug is not None:
        get_partner_or_401(request, partner_slug)
    else:
        member = get_object_or_404(PatreonMemberID, id=member_id, user=request.user)
    if member is None:
        member = get_object_or_404(PatreonMemberID, id=member_id)

    data = member.get_member_data()
    for pledge in data['included']:
        if pledge['type'] == "pledge-event":
            (dbpledge, created) = PledgeData.objects.get_or_create(campaign=member.campaign,
                                                                   id=pledge['id'],
                                                                   date=pledge['attributes']['date'],
                                                                   type=pledge['attributes']['type']
                                                                   )

            tier_title = pledge['attributes']['tier_title']
            if tier_title is None:
                tier_name = "Follower (non-patron)"
            else:
                tier_name = tier_title
            tier, _ = SubscriptionTier.objects.get_or_create(campaign=member.campaign.subscription_campaign,
                                                             external_name=tier_title,
                                                             tier_name=tier_name)

            dbpledge.user = member.user
            dbpledge.tier = tier
            dbpledge.payment_status = pledge['attributes']['payment_status']
            dbpledge.pledge_payment_status = pledge['attributes']['pledge_payment_status']
            dbpledge.save()
    return JsonResponse(member.get_member_data())
