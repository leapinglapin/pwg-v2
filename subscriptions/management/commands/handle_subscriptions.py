import time
import traceback

from dateutil import tz
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from allauth.socialaccount.models import SocialToken
from patreonlink.models import PatreonCampaign
from datetime import datetime, timedelta

from subscriptions.models import SubscriberList, SubscriptionCampaign

sleep_time = 60  # 1 minute


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--start_campaign', type=int)

    def handle(self, *args, **options):
        while True:
            campaigns = SubscriptionCampaign.objects.all().order_by('name')
            if options['start_campaign']:
                start = options['start_campaign']
                campaign_list = [campaigns[start]]
                first_campaign = campaigns[start]
                for campaign in campaigns.exclude(id=first_campaign.id):
                    campaign_list.append(campaign)
            else:
                campaign_list = campaigns
            for subscription_campaign in campaign_list:
                (purchase_count, user_count,
                 pack_count) = subscription_campaign.check_pledges_to_populate_downloads()
                print("{} purchases created from {} packs".format(purchase_count, pack_count))
            wake_time = datetime.now() + timedelta(seconds=sleep_time)
            print("Finished at " + str(datetime.now()))
            print("Waiting until " + str(wake_time.astimezone(tz=tz.tzlocal())))
            time.sleep(sleep_time)
