from django.urls import path
from .views import *

urlpatterns = [
    path('saved_cards/', saved_cards, name='saved_cards'),
    path('remove_card/<card_id>', remove_card, name='remove_card'),
    path('default_address/', default_address, name='default_address')
]
