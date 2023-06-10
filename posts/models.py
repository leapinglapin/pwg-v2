from django.db import models

# Create your models here.
from wagtail.fields import RichTextField


class Post(models.Model):
    partner = models.ForeignKey('partner.Partner', on_delete=models.CASCADE)
    release_time = models.DateTimeField()
    content = RichTextField(blank=True, null=True, features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul'])

    games = models.ManyToManyField('game_info.Game')
    editions = models.ManyToManyField('game_info.Edition')
    formats = models.ManyToManyField('game_info.Format')
    factions = models.ManyToManyField('game_info.Faction')
    attributes = models.ManyToManyField('game_info.Attribute')
    products = models.ManyToManyField('shop.Product')


class Banner(models.Model):
    partner = models.ForeignKey('partner.Partner', on_delete=models.CASCADE)
    image = models.ForeignKey('images.Image', on_delete=models.SET_NULL, blank=True, null=True)
    banner_overlay_text = RichTextField()
    button_text = models.CharField(max_length=255, blank=True)
    button_link = models.CharField(max_length=512,
                                   blank=True)
    alignment = models.CharField(max_length=6,
                                 choices=[
                                     ('left', "Left aligned"),
                                     ('center', "Centered"),
                                     ('right', "Right aligned")
                                 ],
                                 default='left')

    banner_priority = models.IntegerField(default=0, help_text="Higher banner appear earlier in series")
    draft = models.BooleanField(default=True)
    show_on_platform = models.BooleanField(default=True, help_text="Show on CG&T")
    show_on_individual_site = models.BooleanField(default=True, help_text="If you have a custom site")
    on_site_priority = models.IntegerField(default=0, help_text="Higher banner appear earlier in series")
