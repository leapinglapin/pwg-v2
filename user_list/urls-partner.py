from django.urls import path, include

from . import views

urlpatterns = [
    path('<partner_slug>/user_lists/', views.manage_lists, name='manage_lists'),
    path('<partner_slug>/user_lists/create/', views.create_edit_list, name='create_user_list'),
    path('<partner_slug>/user_lists/edit/<int:list_id>/', views.create_edit_list, name='edit_user_list'),
    path('<partner_slug>/user_lists/view/<int:list_id>/', views.view_user_list, name='view_user_list'),

    path('<partner_slug>/user_lists/remove_entry/<int:ule_id>/', views.remove_user_endpoint, name='user_list_remove_user'),
    path('<partner_slug>/user_lists/delete_inv/<int:inv_id>/', views.delete_invitation_endpoint, name='user_list_delete_inv'),

]
