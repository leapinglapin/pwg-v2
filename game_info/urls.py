from django.urls import path, include

from . import views

urlpatterns = [
    path('games/', views.games, name='games'),
    path('game/<slug:game_slug>/', views.game_info, name='game'),
    path('game/faction/<int:faction_id>/', views.faction_info, name='faction'),
    path('game/attribute/<int:attribute_id>/', views.attribute_info, name='attribute'),

]
