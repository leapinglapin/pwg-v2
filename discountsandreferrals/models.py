from django.conf import settings
from django.db import models
from djmoney.models.fields import MoneyField


class Referrer(models.Model):
    administrators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    name = models.CharField(max_length=200)


class ReferrerTransaction(models.Model):
    datetime = models.DateTimeField()
    amount = MoneyField(max_digits=19, decimal_places=2, null=True, default_currency='USD')
    cart = models.ForeignKey("checkout.Cart", on_delete=models.CASCADE)


class CodeSeries(models.Model):
    referrer = models.ForeignKey("Referrer", on_delete=models.CASCADE)
    prefix = models.CharField(max_length=40, unique=True)


class Code(models.Model):
    series = models.ForeignKey("CodeSeries", on_delete=models.CASCADE)
    suffix = models.CharField(max_length=40)

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(fields=['series', 'suffix'], name='no_duplicate_codes')
        ]


class Discount(models.Model):
    partner = models.ForeignKey("partner.Partner", on_delete=models.CASCADE)
    series = models.ForeignKey("CodeSeries", on_delete=models.CASCADE)

    free_shipping = models.BooleanField(default=False)
    free_shipping_minimum = MoneyField(max_digits=19, decimal_places=2, null=True, default_currency='USD')
    discount_percentage = models.DecimalField(default=0, decimal_places=2, max_digits=2)
    kickback_percentage = models.DecimalField(default=0, decimal_places=2, max_digits=2)
