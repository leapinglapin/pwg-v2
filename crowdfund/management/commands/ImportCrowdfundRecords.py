import sys
from inspect import getmembers

import pandas
from django.core.management.base import BaseCommand, CommandError

from crowdfund.models import CrowdfundCampaign, Reward, Backer, CrowdfundTier



class Command(BaseCommand):
    help = "imports the records from a kickstarter"

    def add_arguments(self, parser):
        parser.add_argument('Campaign Name', type=str)
        parser.add_argument('File Path', type=str)

    def handle(self, *args, **options):
        search = options['Campaign Name']
        if not search:
            print("Please specify the campaign")
            return
        campaigns = CrowdfundCampaign.objects.filter(name__search=search)

        campaign = None
        if campaigns.count() == 1:
            campaign = campaigns.first()
            print(campaign)
        else:
            print("Please choose a campaign:")
            print(campaigns)
            return

        file_path = options['File Path']

        dataframe = pandas.read_csv(file_path, header=0)

        records = dataframe.fillna(0).to_dict(orient='records')
        print("Importing all records")

        for record in records:
            print(record)
            backing_minimum = record['Backing Minimum']
            if type(backing_minimum) is str:
                backing_minimum = float(backing_minimum[1:])

            pledge_amount = record['Pledge Amount']
            if pledge_amount:
                pledge_amount = float(pledge_amount[1:])
            if pledge_amount > 0:
                tier = None
                if record['Reward Title']:
                    tier, _ = CrowdfundTier.objects.get_or_create(
                        campaign=campaign,
                        name=record['Reward Title']
                    )

                backer, _ = Backer.objects.get_or_create(
                    campaign=campaign,
                    email_address=record['Email'],
                    backing_minimum=backing_minimum,
                    pledge_amount=pledge_amount,
                    tier=tier,
                )
                backer.rewards.clear()
                for reward_name in list(record.keys())[15:]:
                    if record[reward_name]:
                        print("User entitled to {}".format(reward_name))
                        reward, _ = Reward.objects.get_or_create(campaign=campaign,
                                                                 external_name=reward_name,
                                                                 defaults={'name': reward_name})
                        backer.rewards.add(reward)

        print("Linking records to users that exist and charge creators")
        linked_count = 0
        backers = Backer.objects.filter(campaign=campaign)
        for backer in backers:
            backer.charge_creator()

            if backer.try_match():
                linked_count += 1
        print("{} users were linked of {} users".format(linked_count, backers.count()))
