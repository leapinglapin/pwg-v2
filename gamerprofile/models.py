from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models

# Create your models here.
from game_info.models import Game


class interest_in_game(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    own = models.BooleanField()

    levels_of_knowledge = models.IntegerChoices([
        "Want to learn",
        "Know the basics",
        "Comfortable playing",
        "Advanced player",
        "Rules Expert"
    ])
    level_of_knowledge = models.IntegerField(levels_of_knowledge)

    levels_of_interest = models.IntegerField([
        "Don't want to play",
        "Not my favorite",
        "Interested in trying",
        "I enjoy it",
        "In my top games",
        "Favorite game",

    ])
    level_of_interest = models.IntegerField(levels_of_knowledge)

    want_a_demo = models.BooleanField()
    will_ron_demos = models.BooleanField()
