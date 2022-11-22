from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.manage_packs, name='manage_pack_products'),
    path('<int:pack_id>/', views.manage_pack, name='manage_pack'),
    path('create/', views.create_edit_pack, name='create_digital_pack'),
    path('edit/<pack_id>/', views.create_edit_pack, name='edit_digital_pack'),
]
