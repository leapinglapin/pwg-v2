import csv
import datetime

import pytz
from django.core.management import BaseCommand
from django.core.paginator import Paginator
from djmoney.money import Money
from tqdm import tqdm

import patreonlink.models
from billing.models import BillingEvent
from digitalitems.models import Downloads


class Command(BaseCommand):

    def handle(self, *args, **options):
        records_without_charges = Downloads.objects.filter(added_from_subscription_pack__isnull=False,
                                                           billing_event__isnull=True, skip_billing=False)
        record_count = records_without_charges.count()
        fieldnames = ["Partner", "Partner Transaction ID", "Pledge ID", "Email", "User", "On Creation?"]
        csvfile = open("reports/non-migrated pt charges.csv", "w")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print("{} records to check for charges".format(record_count))
        i = 0
        # We cannot filter the list by any parameter we update over the query
        # will change where in the page count that object appears.
        paginator = Paginator(Downloads.objects.filter(added_from_subscription_pack__isnull=False)
                              .order_by('id'), 10000)
        print("out of {} records".format(paginator.count))

        pbar = tqdm(total=record_count, unit="records")
        total_count = tqdm(total=paginator.count, unit="records")
        page_bar = tqdm(total=paginator.num_pages, unit="pages")

        for page in paginator.page_range:
            page_bar.update(1)
            for added_download in paginator.page(page).object_list:
                total_count.update(1)
                page_bar.update(0)
                if added_download.billing_event is not None or added_download.skip_billing:
                    # Cannot filter a slice of a query, so we have to skip records manually.
                    pbar.update(0)
                    continue
                pbar.update(1)
                subs_pack = added_download.added_from_subscription_pack
                partner = subs_pack.campaign.partner
                pledge_timestamp = added_download.date  # It's called "date" but it's a timestamp
                user = added_download.user
                charge_timestamp = pledge_timestamp
                user_join_timestamp = user.date_joined
                if charge_timestamp < user_join_timestamp:  # If the pledge is before the date the user joined,
                    charge_timestamp = user_join_timestamp  # Partner is charged on the date the user joined.
                if added_download.timestamp_added:
                    charge_timestamp = added_download.timestamp_added  # If we have more accurate data, use that instead

                # Adjust for patreon's timezone wonkiness, see patreonlink.models.pledgedata.patreon_timestamp
                corrected_pledge_timestamp = pledge_timestamp.astimezone(pytz.timezone('US/Pacific')).replace(
                    tzinfo=None).astimezone(pytz.timezone('UTC')) + datetime.timedelta(seconds=2)

                # 1st day of the month of the pledge (according to patreon)
                pledge_month = corrected_pledge_timestamp.date().replace(day=1)

                if pledge_month < subs_pack.campaign.patreon_campaign.begin_charge_on:
                    added_download.skip_billing = True  # Skip this datapoint for future loops
                    added_download.save()
                    i += 1
                    continue  # proceed to next iteration without making a billing event

                old_pt = None
                pledge = None
                relevant_pledges = patreonlink.models.PledgeData.objects.filter(user=user,
                                                                                qualified_for_packs=subs_pack,
                                                                                date=pledge_timestamp)
                if relevant_pledges.count() == 1:
                    pledge = relevant_pledges.first()  # There should only ever be one pledge with the same timestamp.
                    if pledge.linked_charge:
                        old_pt = pledge.linked_charge

                billing_event_for_this_download = None
                user_events = BillingEvent.objects.filter(user=user, partner=partner).order_by('timestamp')
                month_events = user_events.filter(pledge_month=pledge_month)
                if charge_timestamp.replace(tzinfo=None) < datetime.datetime(2022, 10, 1):
                    # If before october 2022, there is only one charge for multiple packs in a given month
                    # So we create a charge for each month there is a pledge that granted content
                    if not month_events.exists():  # Charge the user once for the month in question

                        billing_event_for_this_download = self.charge_partner(charge_timestamp, user,
                                                                              partner, pledge_month, subs_pack, pledge,
                                                                              old_pt)
                    elif month_events.count() == 1:
                        # Associate this charge with a user
                        billing_event_for_this_download = month_events.first()
                        billing_event_for_this_download.linked_to_packs.add(subs_pack)
                        billing_event_for_this_download.save()
                    else:
                        # We should never have more than one billing statement for a month before october 2022
                        pass
                else:
                    # The new billing system creates a charge for each content grant per month
                    pack_events = month_events.filter(linked_to_packs=subs_pack)
                    if not pack_events.exists():  # If there isn't a charge for the month and pack,
                        # this was an instance of content being added, right?
                        # or will it look at the wrong date on the charge?
                        # Create a new billing event
                        billing_event_for_this_download = self.charge_partner(charge_timestamp, user,
                                                                              partner, pledge_month, subs_pack, pledge,
                                                                              old_pt)

                added_download.billing_event = billing_event_for_this_download
                added_download.save()
                i += 1
        print("\n\n\n\nDone")

    @staticmethod
    def charge_partner(charge_date, user, partner, pledge_month, subs_pack, pledge, old_pt):
        billing_event_for_this_download = BillingEvent.objects.create(
            partner=partner,
            user=user,
            type=BillingEvent.INTEGRATION_CHARGE,
            timestamp=charge_date,
            pledge_month=pledge_month,
            platform_fee=Money('-.10', "USD"),
            final_total=Money('-.10', "USD"),
            migrated_from=old_pt,
        )
        if pledge:
            billing_event_for_this_download.email_at_time_of_event = pledge.email
        billing_event_for_this_download.linked_to_packs.add(subs_pack)
        billing_event_for_this_download.save()
        return billing_event_for_this_download
