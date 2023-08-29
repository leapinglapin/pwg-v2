from django.urls import path
from .views import *
from patreonlink.views import raw_data

urlpatterns = [
    path('pledges/', user_pledge_history, name='user_pledges'),
    path('refresh_from_patreon/<member_id>/', raw_data, name='user_refresh_patreon_pledges'),
]
