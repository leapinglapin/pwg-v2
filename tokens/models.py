from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models, transaction

# Create your models here.
from django.db.models import Q

from partner.models import Partner
from shop.models import Item


class Token(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='tokens')
    name = models.TextField()

    def __str__(self):
        return self.name


class TokenBalance(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='token_balances')
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    balance = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(fields=['user', 'token'], name='one_balance_per_token')
        ]


class TokenTransaction(models.Model):
    balance = models.ForeignKey(TokenBalance, on_delete=models.CASCADE)
    pack = models.ForeignKey('subscriptions.SubscriptionPack', on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey('shop.Item', on_delete=models.SET_NULL, null=True)
    change = models.SmallIntegerField()
    applied = models.BooleanField(default=False)

    def apply(self):
        with transaction.atomic():
            if not self.applied:
                self.balance.balance += self.change
                self.balance.save()
                self.applied = True
                self.save()

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(fields=['balance', 'pack'], condition=~Q(pack=None),
                                                name='one_change_per_pack')
        ]


class TokenCost(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    cost = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(fields=['item', 'token'], name='one_cost_per_token_per_item')
        ]

# class AdditionalSubscriptionTokens(models.Model):
#     """Not used.... yet. I imagine someone will want this at some point"""
#     pack = models.ForeignKey('subscriptions.SubscriptionPack', on_delete=models.CASCADE, null=True)
#     token = models.ForeignKey('Token', on_delete=models.CASCADE)
#     change = models.PositiveSmallIntegerField()
