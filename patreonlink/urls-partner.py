from django.urls import path, include

from . import views

urlpatterns = [
    path('view_raw_data/<member_id>/', views.raw_data, name='patreon_member_raw_data')

]
