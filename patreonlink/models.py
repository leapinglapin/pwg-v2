import datetime

import django.db.utils
import patreon
import pytz
import requests
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from djmoney.money import Money

from partner.models import PartnerTransaction
from subscriptions.models import SubscriptionTier, SubscriptionPack


class PatreonCampaign(models.Model):
    subscription_campaign = models.OneToOneField('subscriptions.SubscriptionCampaign', on_delete=models.CASCADE,
                                                 related_name="patreon_campaign")
    campaign_id = models.CharField(max_length=50, null=True, blank=True)
    creator_access_token = models.CharField(max_length=200)
    creator_refresh_token = models.CharField(max_length=200, null=True)
    client_secret = models.CharField(max_length=200, null=True)
    client_id = models.CharField(max_length=200, null=True)
    token_needs_refreshed = models.BooleanField(default=False)
    refresh_token_needs_refreshed = models.BooleanField(default=False)
    begin_charge_on = models.DateField()
    be_patron_button_number = models.CharField(max_length=20, default=None, blank=True, null=True)
    last_refreshed_token = models.DateTimeField(blank=True, null=True)
    last_data_retrieved = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.subscription_campaign.name)

    def get_campaign_members_and_pledges(self):
        campaign = PatreonCampaign.objects.get(id=self.id)
        access_token = campaign.creator_access_token
        refresh_token = campaign.creator_refresh_token
        api_client = patreon.API(access_token)
        try:
            self.campaign_id = api_client.fetch_campaign().json_data['data'][0]['id']
        except AttributeError:
            self.token_needs_refreshed = True
            try:
                if self.creator_refresh_token:
                    suffix = "token" + \
                             "?grant_type=refresh_token" + \
                             "&refresh_token={}&client_id={}&client_secret={}". \
                                 format(refresh_token,
                                        self.client_id, self.client_secret)
                    response = requests.post(
                        "https://www.patreon.com/api/oauth2/{}".format(suffix),
                        headers={
                            'User-Agent': "Patreon CGT",
                        },
                        timeout=(7, 30)
                    )
                    print(response.json())
                    self.creator_access_token = response.json()['access_token']
                    self.creator_refresh_token = response.json()['refresh_token']
                    self.last_refreshed_token = timezone.now()
                    self.token_needs_refreshed = False
                    self.refresh_token_needs_refreshed = False
            except AttributeError as e:
                self.refresh_token_needs_refreshed = True
        self.save()

        total_members = 1
        cursor = None
        members = []
        pledge_data = []
        while len(members) < total_members:
            suffix = "campaigns/{}/members?include=pledge_history&fields[pledge-event]=" \
                     "date,type,payment_status,pledge_payment_status,tier_title&fields[member]=email," \
                     "last_charge_date,next_charge_date,pledge_cadence,last_charge_status".format(self.campaign_id)
            if cursor:
                suffix += ("&page[cursor]={}".format(cursor))
            response = requests.get(
                "https://www.patreon.com/api/oauth2/v2/{}".format(suffix),
                headers={
                    'Authorization': "Bearer {}".format(access_token),
                    'User-Agent': "Patreon CGT",
                },
                timeout=(7, 30)
            )

            campaign = response.json()
            members += campaign['data']
            self.last_data_retrieved = timezone.now()
            self.token_needs_refreshed = False
            self.refresh_token_needs_refreshed = False
            self.save()
            try:
                pledge_data += campaign['included']
            except KeyError:
                print("\n No pledges on page \n")
            pagination = campaign['meta']['pagination']
            try:
                total_members = pagination['total']
                print("Downloading members {}/{} at {}    "
                      .format(len(members), total_members, timezone.now()),
                      end="\r", flush=True)
                cursor = pagination['cursors']['next']

            except KeyError as e:
                break
        return members, pledge_data

    def get_pledge_history(self):
        members, pledge_data = self.get_campaign_members_and_pledges()
        print("")
        created_count = 0
        total_pledge_data = len(pledge_data)
        processed_pledge_data = 0
        for pledge in pledge_data:
            try:
                (dbpledge, created) = PledgeData.objects.get_or_create(campaign=self,
                                                                       id=pledge['id'],
                                                                       date=pledge['attributes']['date'],
                                                                       type=pledge['attributes']['type']
                                                                       )

                tier_title = pledge['attributes']['tier_title']
                if tier_title is None:
                    tier_name = "Follower (non-patron)"
                else:
                    tier_name = tier_title
                tier, _ = SubscriptionTier.objects.get_or_create(campaign=self.subscription_campaign,
                                                                 external_name=tier_title,
                                                                 tier_name=tier_name)

                dbpledge.tier = tier
                if created:
                    created_count += 1
                dbpledge.payment_status = pledge['attributes']['payment_status']
                dbpledge.pledge_payment_status = pledge['attributes']['pledge_payment_status']
                dbpledge.save()
                processed_pledge_data += 1
                print("Processing pledges {}/{}, {} new pledges processed "
                      .format(processed_pledge_data, total_pledge_data, created_count),
                      end="\r", flush=True)
            except django.db.utils.IntegrityError:
                print("")
                print("Unable to save pledge due to duplicate key or other DB error:")
                print(pledge)
                print("")
            except Exception as e:
                # This is here in case there's some non-integrity error
                print("Unable to save pledge due to other error")
                print(e)
                print(pledge)
                print("")
        print("")
        total_pledge_data = len(members)
        processed_pledge_data = 0
        for member in members:
            email = member['attributes']['email']
            id = member['id']
            onsite_emails = EmailAddress.objects.filter(email__iexact=email)
            user = None
            if onsite_emails.count() == 1:
                user = onsite_emails.first().user
                member_id, _ = PatreonMemberID.objects.get_or_create(campaign=self, id=id, defaults={'user': user})
                if member_id.user != user:
                    member_id.user = user
                member_id.save()
            ph = member['relationships']['pledge_history']
            pledges = ph['data']
            for pledge in pledges:
                try:
                    dbpledge = PledgeData.objects.get(id=pledge['id'])
                    if user:
                        dbpledge.user = user
                    dbpledge.email = email
                    dbpledge.save()
                    # do some annual pledge processing
                    try:
                        if member['attributes']['pledge_cadence'] == 12 and \
                                member['attributes']['last_charge_status'] == "Paid":
                            last_charge_date = datetime.datetime. \
                                fromisoformat(member['attributes']['last_charge_date'])
                            # print(pledgedate, dbpledge.date)
                            tolerance = datetime.timedelta(seconds=3)
                            if last_charge_date - tolerance <= dbpledge.date <= last_charge_date + tolerance:
                                # Found original pledge for annual pledge.
                                pledge_date = dbpledge.date
                                if pledge_date.day > 28:
                                    pledge_date = pledge_date.replace(day=2)
                                for i in range(1, 12):
                                    month = pledge_date.month
                                    year = pledge_date.year
                                    month = month + 1
                                    if month > 12:
                                        month = month - 12
                                        pledge_date = pledge_date.replace(year=year + 1)
                                    pledge_date = pledge_date.replace(month=month)
                                    # Create or update new pledges based on original
                                    new_pledge, created = PledgeData.objects.get_or_create(campaign=self,
                                                                                           id=pledge['id'] + "a" + str(
                                                                                               i),
                                                                                           date=pledge_date,
                                                                                           type=dbpledge.type,
                                                                                           )
                                    if user:
                                        new_pledge.user = user
                                    new_pledge.email = email
                                    new_pledge.tier = dbpledge.tier
                                    new_pledge.status = dbpledge.payment_status
                                    new_pledge.pledge_payment_status = dbpledge.pledge_payment_status
                                    new_pledge.save()
                    except Exception as e:
                        print("Annual pledge check failed")
                        print(e)
                        print(pledge)
                        print("")
                except Exception as e:
                    pass
            processed_pledge_data += 1
            print("Adding emails to pledges {}/{}"
                  .format(processed_pledge_data, total_pledge_data), end="\r", flush=True)
        print("")

    def debug_pledge_vs_members(self):
        members, pledge_data = self.get_campaign_members_and_pledges()
        campaign_pledges_dict = {}
        for included in pledge_data:
            if included['type'] == "pledge-event":
                campaign_pledges_dict[included['id']] = included
        print("")
        included_but_not_ph_count = 0
        included_but_not_campaign_ph_count = 0
        included_but_not_campaign_pledge = 0
        number_included = 0
        valid_count = 0
        total_members = len(members)
        processed_members = 0
        for member in members:
            processed_members += 1
            campaign_member_pledge_history = member['relationships']['pledge_history']['data']

            id = member['id']
            suffix = "members/{}?fields[address]=line_1,line_2,addressee,postal_code,city" \
                     "&fields[member]=full_name,is_follower,last_charge_date,next_charge_date," \
                     "patron_status,pledge_cadence,last_charge_status,currently_entitled_amount_cents" \
                     "&include=address,user,pledge_history".format(id)
            response = requests.get(
                "https://www.patreon.com/api/oauth2/v2/{}".format(suffix),
                headers={
                    'Authorization': "Bearer {}".format(self.creator_access_token),
                    'User-Agent': "Patreon CGT",
                }
            )
            data = response.json()
            member_included_pledges = []
            for included in data['included']:
                if included['type'] == "pledge-event":
                    member_included_pledges.append(included)
            member_pledge_history = []
            try:
                member_pledge_history = data['data']['relationships']['pledge_history']['data']
            except KeyError:
                pass  # Wasn't able to find member_pledge_history

            member_included_dict = {pledge['id']: pledge for pledge in member_included_pledges}
            member_pledge_history_dict = {pledge['id']: pledge for pledge in member_pledge_history}
            campaign_member_pledge_history_dict = {pledge['id']: pledge for pledge in campaign_member_pledge_history}

            number_included += len(member_included_dict)
            for pledge_id in member_included_dict.keys():
                valid = 1
                if pledge_id not in member_pledge_history_dict.keys():
                    print(member_included_dict[pledge_id], "not in member pledge history \n")
                    valid = 0
                    included_but_not_ph_count += 1
                if pledge_id not in campaign_member_pledge_history_dict.keys():
                    print(member_included_dict[pledge_id], "not in campaign reported member pledge history \n")
                    valid = 0
                    included_but_not_campaign_ph_count += 1
                if pledge_id not in campaign_pledges_dict.keys():
                    print(member_included_dict[pledge_id], "not in campaign pledges \n")
                    valid = 0
                    included_but_not_campaign_pledge += 1
                valid_count += valid
            print(("Checking pledges, {} not in member pledge history, {} not in campaign member history, " +
                   "{} not in campaign pledges, {} valid, out of {} from {} members out of {}  ")
                  .format(included_but_not_ph_count, included_but_not_campaign_ph_count,
                          included_but_not_campaign_pledge, valid_count, number_included,
                          processed_members, total_members),
                  end="\r", flush=True)

        print("")


class UnpaidError(Exception):
    pass


class PatreonMemberID(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    campaign = models.ForeignKey(PatreonCampaign, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_member_data(self):
        suffix = "members/{}?fields[address]=line_1,line_2,addressee,postal_code,city" \
                 "&fields[member]=full_name,is_follower,last_charge_date,next_charge_date," \
                 "patron_status,pledge_cadence,last_charge_status,currently_entitled_amount_cents" \
                 "&include=address,user,pledge_history".format(
            self.id)
        response = requests.get(
            "https://www.patreon.com/api/oauth2/v2/{}".format(suffix),
            headers={
                'Authorization': "Bearer {}".format(self.campaign.creator_access_token),
                'User-Agent': "Patreon CGT",
            }
        )

        return response.json()


class PatreonPledgeQuerySet(models.QuerySet):
    def filter_by_user(self, user):
        queryset = self
        primary_email_matches = queryset.filter(email__iexact=user.email)
        account_matches = queryset.filter(user=user)
        user_queryset = primary_email_matches | account_matches
        emails = EmailAddress.objects.filter(user=user)
        for ea in emails:
            user_queryset = user_queryset | queryset.filter(email__iexact=ea.email)
        return user_queryset.distinct()


class PledgeData(models.Model):
    objects = PatreonPledgeQuerySet.as_manager()

    id = models.CharField(primary_key=True, max_length=30)
    date = models.DateTimeField()  # This date is in UTC, but patreon actually cares about the month in california time.
    payment_status = models.CharField(max_length=10, null=True, blank=True)
    pledge_payment_status = models.CharField(max_length=10, null=True, blank=True)
    tier = models.ForeignKey('subscriptions.SubscriptionTier', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=20)
    campaign = models.ForeignKey(PatreonCampaign, on_delete=models.CASCADE)
    email = models.CharField(max_length=200, null=True, blank=True)
    linked_charge = models.ForeignKey(PartnerTransaction, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="linked_pledge")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    ignore = models.BooleanField(default=False)

    qualified_for_packs = models.ManyToManyField(SubscriptionPack, related_name='qualifying_patreon_pledges')

    MANUAL = "manual"
    PLEDGE_START = "pledge_start"
    PLEDGE_UPGRADE = "pledge_upgrade"
    PLEDGE_DOWNGRADE = "pledge_downgrade"
    SUBSCRIPTION = "subscription"

    # The states that we are supposed to see for payment_status
    PAID, DECLINED, DELETED, PENDING, REFUNDED, FRAUD, OTHER = (
        "Paid", "Declined", "Deleted", "Pending", "Refunded", "Fraud", "Other")

    # Undocumented states we've found for pledge_payment_status
    PPS_VALID = "valid"
    PPS_DECLINED = "declined"

    def __str__(self):
        return "{} {} {} {}".format(self.date, self.email, self.tier, self.campaign.subscription_campaign.name)

    def get_user(self):
        user = self.user
        if user is None:
            user = User.objects.filter(email__iexact=self.email).first()
            if user is None:
                onsite_emails = EmailAddress.objects.filter(email__iexact=self.email)
                if onsite_emails.count() == 1:
                    user = onsite_emails.first().user
        return user

    def confirm_in_timeframe(self, start, end):
        patreon_pledge_time = self.patreon_timestamp()
        if start <= patreon_pledge_time <= end:
            # Ensure pledge is in the correct date range
            return True
        else:
            return False

    def confirm_paid(self, debug=False):
        if debug:
            print(
                "{}: ignore: {}, type:{}, payment_status: {}".format(self, self.ignore, self.type, self.payment_status))
        if self.ignore:  # Always ignore ignored
            return False
        if self.type in [self.MANUAL, self.PLEDGE_DOWNGRADE]:
            return True  # Always return true for manual pledges
            # And downgrade pledges since a downgrade should count as paid.

        if self.type in [self.PLEDGE_START, self.PLEDGE_UPGRADE, self.PLEDGE_DOWNGRADE]:
            return self.pledge_payment_status == self.PPS_VALID
        return self.type == self.SUBSCRIPTION and self.payment_status == self.PAID

    def charge_creator(self):
        """
        If there is no linked charge associated with this pledge, charge the partner associated 10c.
        """
        if self.date.date() < self.campaign.begin_charge_on:
            return  # if before the date where we start charging, don't charge.
        if self.linked_charge is None:
            self.linked_charge = PartnerTransaction.objects.create(partner=self.campaign.subscription_campaign.partner,
                                                                   type=PartnerTransaction.PLATFORM_CHARGE,
                                                                   transaction_total=Money(0, 'USD'),
                                                                   transaction_subtotal=Money(0, 'USD'),
                                                                   transaction_fees=Money(".10", 'USD'))
            self.linked_charge.timestamp = self.date  # Override timestamp, can't be done at create
            self.linked_charge.save()
            self.linked_charge.apply()
            self.save()

    def patreon_timestamp(self):
        """
        This function returns the date as patreon would see it, shifted by 2 seconds to ensure it's in the proper month.
        :return: time at patreon +2 second
        """
        return self.date.astimezone(pytz.timezone('US/Pacific')).replace(tzinfo=None) \
            .astimezone(pytz.timezone('UTC')) + datetime.timedelta(seconds=2)
