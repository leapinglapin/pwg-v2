import datetime

from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models

from djmoney.models.fields import MoneyField

from digitalitems.models import DigitalItem
from shop.models import Product, Item


class DigitalPack(Product):
    pack_contents = models.ManyToManyField(DigitalItem, blank=True, related_name="packs")
    suggested_contents = models.ManyToManyField(DigitalItem, blank=True)
    price = MoneyField(max_digits=8, decimal_places=2, default_currency='USD', null=True)
    default_price = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')
    enable_discounts = models.BooleanField(default=True)

    pay_what_you_want = models.BooleanField(default=False,
                                            help_text="This makes price the minimum the user has to pay, "
                                                      "and default price the amount the form defaults to")

    grant_to_user_lists = models.ManyToManyField("user_list.UserList", related_name='digital_packs', blank=True)

    grant_to_subscriptions = models.ManyToManyField("subscriptions.SubscriptionPack", related_name="digital_packs",
                                                    blank=True)

    grant_to_crowdfund_rewards = models.ManyToManyField("crowdfund.Reward", related_name="digital_packs", blank=True)

    def save(self, *args, **kwargs):
        super(DigitalPack, self).save(*args, **kwargs)

        item, created = PackItem.objects.get_or_create(product=self, defaults={'price': self.price,
                                                                               "default_price": self.default_price,
                                                                               'partner': self.partner
                                                                               })

        item.price = self.default_price
        item.pay_what_you_want = self.pay_what_you_want
        item.default_price = self.default_price
        item.enable_discounts = self.enable_discounts
        item.partner = self.partner
        item.save()

    def populate_users_downloads(self, user):
        # if self.grant_to_user_lists.objects.filter(grant_to_user_lists=UserList.lists.groups_for_user(user)).exists:
        if user.backer_records.filter(rewards__in=self.grant_to_crowdfund_rewards.all()).exists():
            for item in self.pack_contents.all():
                if not item.downloads.filter(user=user).exists():  # Purchase does not already exist
                    try:
                        # Create purchase
                        item.downloads.create(user=user, item=item,
                                              date=datetime.datetime.now(),
                                              partner_paid=True,
                                              added_from_digital_pack=self)
                        print("Added {} to {}'s downloads".format(item, user))
                    except Exception as e:
                        print(e)


class PackItem(Item):
    pay_what_you_want = models.BooleanField(default=False,
                                            help_text="This makes price the minimum the user has to pay, "
                                                      "and default price the amount the form defaults to")

    def purchase(self, cart):
        packEntitlement, created = self.product.PackEntitlements.get_or_create(user=cart.owner,
                                                                               defaults={"date": cart.date_submitted,
                                                                                         "added_from_cart": cart})
        for item in self.product.pack_contents.all():
            item.purchase(cart)

    def user_already_owns(self, user):
        return not user.is_anonymous and len(self.product.PackEntitlements.filter(user=user)) > 0


class PackEntitlement(models.Model):
    pack = models.ForeignKey(DigitalPack, on_delete=models.CASCADE, related_name='PackEntitlements')
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='PackEntitlements')
    date = models.DateTimeField(blank=True, null=True)
    added_from_cart = models.ForeignKey('checkout.Cart', on_delete=models.PROTECT,
                                        related_name='GrantedPackEntitlements')
