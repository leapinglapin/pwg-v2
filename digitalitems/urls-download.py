from django.urls import path

from . import views

urlpatterns = [
    path('<di_id>/<di_file_id>/', views.download, name='digital_download'),
    path('multi/<di_id>/<downloadable_id>/', views.download_multi, name='digital_download_multi'),

]
