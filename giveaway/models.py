from django.contrib.auth.models import User
from django.db import models


class Giveaway(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE)
    end_time = models.DateTimeField()


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    giveaway = models.ForeignKey(Giveaway, on_delete=models.CASCADE)
    time_of_entry = models.DateTimeField(auto_now_add=True)
    one_entry_per_user_constraint = models.UniqueConstraint(fields=('user', 'giveaway'),
                                                            name='one_entry_per_user')
