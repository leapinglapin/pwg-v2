from django.urls import path
from .views import *

urlpatterns = [
    path('', past_orders, name='past_orders'),

    path('<int:cart_id>/', past_order_details, name='past_order_details'),

    path('<int:cart_id>/cancelled/', past_order_mark_cancelled, name='past_order_mark_cancelled'),

]
