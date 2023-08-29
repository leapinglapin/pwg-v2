from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from subscriptions.models import SubscriptionCampaign
from patreonlink.models import PledgeData, PatreonMemberID


@login_required
def user_pledge_history(request):
    campaigns = {}
    for campaign in SubscriptionCampaign.objects.all():
        member_id = PatreonMemberID.objects.filter(campaign__subscription_campaign=campaign, user=request.user).first()
        if member_id:
            patreon_pledges = PledgeData.objects.filter(campaign__subscription_campaign=campaign).order_by('date') \
                .filter_by_user(request.user)
            campaigns[campaign] = {}
            campaigns[campaign]['patreon_pledges'] = patreon_pledges
            campaigns[campaign]['member_id'] = member_id
    context = {
        'campaigns': campaigns
    }
    return render(request, "userinfo/pledges.html", context)
