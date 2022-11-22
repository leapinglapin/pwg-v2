from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='view_packs'),
    path('campaign/<slug:campaign_slug>/', views.view_campaign, name='view_campaign'),
    path('campaign/<slug:campaign_slug>/subscribe/', views.onboarding, name='subscribe_to_campaign'),

    path('campaign/<slug:campaign_slug>/<int:pack_id>', views.view_pack, name='view_pack'),
    path('partner/<slug:partner_slug>/<int:pack_id>/', views.view_pack, name='view_pack'),
    # Left in to not break old links
    path('download/<pack_id>/', views.download_pack, name='download_pack'),

]
