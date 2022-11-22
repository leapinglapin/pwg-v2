from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.manage_subscriptions, name='manage_subscriptions'),
    path('<int:campaign_id>/patreon_api_info/', views.edit_patreon_api_view, name='edit_patreon_api_info'),
    path('<int:campaign_id>/create_subscription_pack/', views.edit_pack, name='create_subscription_pack'),
    path('<int:campaign_id>/view_pack/<int:pack_id>/', views.view_pack_manage, name='view_pack_manage'),
    path('<int:campaign_id>/edit_pack/<int:pack_id>/', views.edit_pack, name='edit_pack'),
    path('<int:campaign_id>/edit_pack/<int:pack_id>/delete/<int:confirm>/', views.delete_pack, name='delete_pack'),
    path('<int:campaign_id>/edit_pack/<int:pack_id>/img/upload/', views.upload_pack_image, name='upload_pack_image'),
    path('<int:campaign_id>/edit_pack/<int:pack_id>/img/delete/<image_id>', views.remove_image,
         name='remove_pack_image'),
    path('<int:campaign_id>/create_discount/', views.edit_discount, name='create_discount'),
    path('<int:campaign_id>/edit_discount/<int:discount_id>/', views.edit_discount, name='edit_discount'),
    path('<int:campaign_id>/edit_discount/<int:discount_id>/delete/<int:confirm>/', views.delete_discount,
         name='delete_discount'),
    path('<int:campaign_id>/create_tier/', views.edit_tier, name='create_tier'),
    path('<int:campaign_id>/edit_tier/<int:tier_id>/', views.edit_tier, name='edit_tier'),
    # path('<int:campaign_id>/edit_tier/<int:tier_id>/delete/<int:confirm>/', views.delete_tier,
    #      name='delete_tier'),
    path('grant_manual_acesss/<int:customer_id>/', views.grant_manual_access, name='grant_manual_access'),
    path('revoke_manual_acesss/<int:customer_id>/', views.revoke_manual_access, name='revoke_manual_access'),

]
