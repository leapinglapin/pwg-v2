from django.db import models

# Create your models here.
import shop.models


class Event(models.Model):
    name = models.TextField()
    start_time = models.DateTimeField()

    game = models.ForeignKey('game_info.Game', blank=True, null=True, on_delete=models.SET_NULL)
    edition = models.ForeignKey('game_info.Edition', blank=True, null=True, on_delete=models.SET_NULL)
    format = models.ForeignKey('game_info.Format', blank=True, null=True, on_delete=models.SET_NULL)


class EventTicketItem(shop.models.Item):
    event = models.ForeignKey('Event', blank=True, null=True, on_delete=models.SET_NULL)
