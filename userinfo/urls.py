from django.urls import path
from .views import *

urlpatterns = [
    path('user_pledge_history/', user_pledge_history, name='saved_cards')
]
