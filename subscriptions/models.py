import datetime

import stripe
from allauth.account.models import EmailAddress
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from djmoney.models.fields import MoneyField
from djmoney.money import Money
from wagtail.core.fields import RichTextField

from checkout.models import StripePaymentIntent
from digitalitems.models import DigitalItem
from partner.models import Partner, PartnerTransaction
from shop.models import Product, Item
from tokens.models import TokenTransaction, TokenBalance


class SubscriptionCampaign(models.Model):
    name = models.CharField(max_length=200)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, related_name='campaigns')
    description = RichTextField()
    slug = models.SlugField(unique=True, blank=True, max_length=200)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(SubscriptionCampaign, self).save(*args, **kwargs)

    def process(self):
        # TODO: process subscriptions
        if hasattr(self, 'patreon_campaign'):
            pass
            # unsure if we need to do anything with patreon subs or just leave the old script running.

    def check_pledges_to_populate_downloads(self, user=None):
        purchase_count = 0
        user_count = 0
        pack_count = 0
        for pack in SubscriptionPack.objects.filter(campaign=self).order_by('pledges_from'):
            (purchase_count_tmp, user_count_tmp) = pack.check_pledges_to_populate_downloads(user)
            purchase_count += purchase_count_tmp
            user_count += user_count_tmp
            pack_count += 1
        return purchase_count, user_count, pack_count


class SubscriptionTier(models.Model):
    campaign = models.ForeignKey(SubscriptionCampaign, on_delete=models.CASCADE, related_name="tiers")
    tier_name = models.CharField(max_length=100, default='Follower')
    external_name = models.CharField(max_length=100, null=True)

    price = MoneyField(max_digits=19, decimal_places=2, null=True)
    default_price = MoneyField(max_digits=19, decimal_places=2, null=True)

    limit = models.IntegerField(default=None, blank=True, null=True)

    allow_on_site_subscriptions = models.BooleanField(default=False)

    class Meta:
        unique_together = [['campaign', 'tier_name'],
                           ['campaign', 'external_name']]
        ordering = ['tier_name']

    def __str__(self):
        if self.tier_name is not None:
            if self.price is not None:
                return self.tier_name + " " + str(self.price)
            return self.tier_name
        else:
            return "Non-Patrons (Followers)"


class SubscriberList(models.Model):
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    payment_method = models.CharField(max_length=40)
    start_date = models.DateField(default=datetime.date.today)

    def save(self, *args, **kwargs):
        for sub in SubscriberList.objects.filter(tier__in=self.tier.campaign.tiers.all(), user=self.user):
            sub.delete()
        super(SubscriberList, self).save(*args, **kwargs)


class SubscriptionData(models.Model):
    # subscription_list_entry = models.ForeignKey(SubscriberList, on_delete=models.SET_NULL, null=True)
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    PAYMENT_ERROR = "ERROR"
    UNPAID = "UNPAID"
    PAYMENT_STATUS_OPTIONS = [
        ("Paid", PAID),
        ("Processing", PROCESSING),
        ("Payment Error", PAYMENT_ERROR),
        ('Unpaid', UNPAID),
    ]
    cart = models.ForeignKey('checkout.Cart', on_delete=models.SET_NULL, null=True)
    error_details = models.TextField()
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_OPTIONS, default=UNPAID)

    def get_item(self, month):
        product, _ = SubscriptionProduct.objects.get_or_create(tier=self.tier, month=month,
                                                               partner=self.tier.campaign.partner)
        item, _ = SubscriptionItem.objects.get_or_create(product=product, tier=self.tier,
                                                         partner=self.tier.campaign.partner)
        return item

    def mark_paid(self):
        self.payment_status = self.PAID
        for pack in SubscriptionPack.objects.filter(tier_req=self.tier):
            pack.check_pledges_to_populate_downloads(user=self.user)
        self.save()


class SubscriptionPack(models.Model):
    campaign = models.ForeignKey(SubscriptionCampaign, on_delete=models.CASCADE, related_name='packs')

    pack_image = models.ForeignKey('shop.ProductImage', on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    contents = models.ManyToManyField(DigitalItem, blank=True, related_name="subscription_packs")
    pack = models.ForeignKey('packs.DigitalPack', on_delete=models.SET_NULL, null=True, blank=True)
    # Leave contents for backwards compatibility until after data migration

    pledges_from = models.DateTimeField()
    pledges_to = models.DateTimeField()
    tier_req = models.ManyToManyField('subscriptions.SubscriptionTier')

    token = models.ForeignKey('tokens.Token', on_delete=models.SET_NULL, null=True, blank=True)
    token_quantity = models.PositiveSmallIntegerField(null=True, blank=True)

    require_multiple_months = models.BooleanField(default=False)
    number_of_months = models.IntegerField(blank=True, null=True)
    require_exact_months = models.BooleanField(default=False)

    user_list = models.ForeignKey("user_list.UserList", on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if self.require_multiple_months and self.require_exact_months:
            self.pledges_from = self.pledges_to - relativedelta(months=self.number_of_months - 1)
        self.pledges_from = self.pledges_from.replace(day=1)
        self.pledges_to = self.pledges_to.replace(day=1)
        if self.token_quantity is None:
            self.token = None
        super(SubscriptionPack, self).save(*args, **kwargs)

    def __str__(self):
        name = str(self.campaign) + " " \
               + str(self.pledges_from.month) + "/" + str(self.pledges_from.year)
        if self.name:
            name += " " + self.name
        return name

    def display_end_time(self):
        return self.pledges_to - datetime.timedelta(seconds=1)

    def count_total_months_subscribed_in_period(self, user, queryset=None):
        if user is None:
            return 0
        count = 0
        tier_filter = self.tier_req.all()
        pledges = SubscriptionData.objects.filter(timestamp__gte=self.pledges_from,
                                                  timestamp__lte=self.pledges_to,
                                                  tier__in=tier_filter,  # Filtering by tier also filters by campaign
                                                  user=user)

        months = []
        for pledge in pledges:
            if pledge.confirm_paid():
                month_stamp = str(pledge.date.year) + str(pledge.date.month)
                if month_stamp not in months:
                    months.append(month_stamp)
                    count += 1

        return count


    def check_pledges_to_populate_downloads(self, user=None, debug=False):
        purchase_count = 0
        total_pledges = 0
        user_count = 0
        unknown_email = 0
        unpaid = 0
        created = 0
        valid = 0
        tier_filter = self.tier_req.all()
        print("Making purchases for pack {} from {}".format(self.name, self.campaign))
        # for user_list in self.auto_grant_to_user_lists.all():
        #     for entry in user_list:
        #         created = self.add_to_downloads_for_user(entry.user, date=datetime.datetime.now())

        # queryset = SubscriptionData.objects.filter(timestamp__gte=self.pledges_from, timestamp__lte=self.pledges_to,
        #                                            tier__in=tier_filter, payment_status=SubscriptionData.PAID,
        #                                            )  # Tier filters by campaign, so we don't need to filter that.
        # if user is not None:
        #     queryset = queryset.filter(user=user)
        #     total_pledges = len(queryset)
        #     for pledge in queryset:
        #         if self.require_multiple_months:
        #             if self.number_of_months > self.count_total_months_subscribed_in_period(pledge.user):
        #                 continue  # Skip this pledge
        #         created = self.add_to_downloads_for_user(pledge.user, date=pledge.timestamp)
        #         valid += 1
        #         print("Processed {}/{}, {} purchases created".format(
        #             valid, total_pledges, created),
        #             end="\r",
        #             flush=True)
        #         purchase_count += created

        if hasattr(self.campaign, 'patreon_campaign'):
            not_in_timeframe = 0
            print("Checking Patreon")
            # Now checks +/- 1 day to ensure we're in the proper timezone.

        if total_pledges != 0:
            print("")
        else:
            print("No eligible pledges found for this pack")
        return purchase_count, user_count

    def add_to_downloads_for_user(self, user, date):
        """
        Only call this function if you know this pledge already falls within the requirements of the pack.
        Does no validation.
        :param user: the user to create
        :param date: the date to log this purchase as
        :return: success_count : the number of purchases created.
        """
        success_count = 0
        if user is None:
            return 0, 0  # consider throwing an error here instead, as this should never be called without a user.
        for item in self.contents.all():
            if not item.downloads.filter(user=user).exists():  # Purchase does not already exist
                try:
                    # Create purchase
                    item.downloads.create(user=user, item=item, date=date, partner_paid=True,
                                          added_from_subscription_pack=self)
                except Exception:
                    pass
                success_count += 1
        if self.token:
            balance, _ = TokenBalance.objects.get_or_create(user=user, token=self.token)
            transaction, created = TokenTransaction.objects.get_or_create(balance=balance,
                                                                          pack=self,
                                                                          defaults={'change': self.token_quantity}
                                                                          )
            transaction.apply()
        return success_count


class SubscriberDiscount(models.Model):
    campaign = models.ForeignKey(SubscriptionCampaign, on_delete=models.CASCADE, related_name='discounts')
    tier_req = models.ManyToManyField(SubscriptionTier)
    price_multiplier = models.DecimalField(max_digits=3, decimal_places=2)

    start_month = models.DateField()
    day_of_month_start = models.IntegerField()
    day_of_month_end = models.IntegerField(help_text="Inclusive of the day")
    repeat = models.BooleanField()

    paused = models.BooleanField(default=False)
    last_month_before_pause = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.start_month = self.start_month.replace(day=1)
        if self.last_month_before_pause:
            self.last_month_before_pause = self.last_month_before_pause.replace(day=1)
        super(SubscriberDiscount, self).save(*args, **kwargs)

    def get_discount_multiplier(self, user):
        if self.is_active_subscriber_during_discount(user):
            return self.price_multiplier
        else:
            return 1

    def is_active_subscriber(self, user):
        if hasattr(self.campaign, 'patreon_campaign'):
            return self.is_active_patron(user)
        month = datetime.date.today()
        if self.paused:
            month = self.last_month_before_pause
        pledge = SubscriptionData.objects.filter(user=user,
                                                 date__gte=month.replace(day=1),
                                                 tier__in=self.tier_req.all(), campaign=self.campaign) \
            .order_by('-date').first()
        if pledge is not None and pledge.confirm_paid:
            return True
        return False

    def is_active_subscriber_during_discount(self, user):
        if self.is_during_discount() and self.is_active_subscriber(user):
            return True
        return False

    def is_during_discount(self):
        today = datetime.date.today()
        if self.start_month.year < today.year or (
                self.start_month.year == today.year and
                self.start_month.month <= today.month):
            if (not self.repeat) and self.day_of_month_end < today.day:
                # If the discount has ended (and is not repeating), return false
                return False
            # If past the start month and in the specified date range, return true
            if self.day_of_month_start <= today.day <= self.day_of_month_end:
                return True
        return False

    def __str__(self):
        percent = (1 - self.price_multiplier) * 100
        title = "{}% off from day {} to day {} starting {}".format(percent, self.day_of_month_start,
                                                                   self.day_of_month_end,
                                                                   self.start_month)
        if self.repeat:
            title += " and repeating each month"
        return title

    def time_remaining(self):
        last_day_of_month = get_last_day_of_month(self.day_of_month_end)

        return datetime.datetime.combine(
            last_day_of_month,
            datetime.time(hour=23, minute=59, second=59)
        ) - datetime.datetime.utcnow()


def get_last_day_of_month(end_of_range):
    try:
        return datetime.date.today().replace(day=end_of_range)
    except ValueError:
        return get_last_day_of_month(end_of_range=end_of_range - 1)


class SubscriptionProduct(Product):
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE, related_name="products")
    month = models.DateField()

    def save(self, *args, **kwargs):
        self.name = "{}: {}: {}/{}".format(self.tier.campaign, self.tier, self.month.year, self.month.month)
        super(SubscriptionProduct, self).save(*args, **kwargs)


class SubscriptionItem(Item):
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE, related_name='items')

    def save(self, *args, **kwargs):
        self.default_price = self.tier.default_price
        self.price = self.tier.price
        super(SubscriptionItem, self).save(*args, **kwargs)
