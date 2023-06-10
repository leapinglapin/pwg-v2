from django.contrib.auth.models import User
from django.db import models, transaction

# Create your models here.
from djmoney.models.fields import MoneyField


class UserCredit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    partner = models.ForeignKey('partner.Partner', on_delete=models.CASCADE, null=True, blank=True)
    balance = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(fields=['user', 'partner'], name='one_balance_per_user_per_partner')
        ]


class UserCreditChange(models.Model):
    balance = models.ForeignKey(UserCredit, on_delete=models.CASCADE)
    change = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')
    applied = models.BooleanField(default=False)

    def apply(self):
        with transaction.atomic:
            if not self.applied:
                self.balance.balance += self.change
                self.balance.save()
                self.applied = True
                self.save()
