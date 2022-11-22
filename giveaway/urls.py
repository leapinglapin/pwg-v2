from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.giveaways, name='giveaways'),
    path('<int:giveaway_id>', views.enter_giveaway, name='enter_giveaway'),
]
