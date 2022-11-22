from django.urls import path

from . import views

urlpatterns = [
    path('digital/add/', views.add_digital, name='digital_add_mng'),
    path('digital/<di_id>/edit/', views.edit_digital, name='digital_edit_mng'),
    path('digital/<di_id>/delete/<int:confirm>/', views.delete_digital, name='digital_delete_mng'),
    path('digital/upload/<di_id>/<parent_node_id>/newfile/', views.upload_file, name='digital_upload_file_mng'),
    path('digital/<di_id>/remove/<di_file_id>/', views.remove_file, name='digital_remove_file_mng'),
    path('digital/<di_id>/remove/multi/<downloadable_id>/', views.remove_downloadable, name='digital_remove_folder_mng'),

]
