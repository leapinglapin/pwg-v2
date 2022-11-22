from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.manage_tokens, name='manage_tokens'),
    path('add/', views.edit_token, name='add_token'),
    path('edit/<int:token_id>/', views.edit_token, name='edit_token'),

]
