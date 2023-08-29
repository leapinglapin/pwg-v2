import time
import traceback

from dateutil import tz
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from patreonlink.models import PatreonCampaign
from datetime import datetime, timedelta

client_id = settings.PATREON_CLIENT_ID
client_secret = settings.PATREON_CLIENT_SECRET
creator_id = None  # Replace with your data

sleep_time = 60  # 1 minute


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--start_campaign', type=int)

    def handle(self, *args, **options):
        while True:
            campaigns = PatreonCampaign.objects.all().order_by('subscription_campaign__name')
            if options['start_campaign']:
                start = options['start_campaign']
                campaign_list = [campaigns[start]]
                first_campaign = campaigns[start]
                for campaign in campaigns.exclude(id=first_campaign.id):
                    campaign_list.append(campaign)
            else:
                campaign_list = campaigns
            for patreon in campaign_list:
                try:
                    print("Getting data for " + str(patreon))
                    patreon.debug_pledge_vs_members()
                except Exception as e:
                    print(e)
                    traceback.print_exc()
            wake_time = datetime.now() + timedelta(seconds=sleep_time)
            print("Finished at " + str(datetime.now()))
            print("Waiting until " + str(wake_time.astimezone(tz=tz.tzlocal())))
            time.sleep(sleep_time)
