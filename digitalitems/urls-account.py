from django.urls import path

from . import api_views
from . import views

urlpatterns = [
    path('downloads/', views.account_downloads, name='account_downloads'),
    path('downloads/<int:refresh>', views.account_downloads, name='account_downloads'),

    path('downloadsv2/', api_views.account_downloads_v2, name='downloads_v2'),
    path('downloadsv2/<int:refresh>', api_views.account_downloads_v2, name='downloads_v2'),

    path('refresh_downloads/<int:user_id>', views.refresh_downloads, name='refresh_downloads'),
]
