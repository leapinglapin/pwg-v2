from django.urls import path

from discount_codes.views import apply_code
from .views import *

urlpatterns = [
    path('', view_cart, name='view_cart'),
    path('cart/', json_cart, name='json_cart'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/<int:quantity>/', update_quantity, name='cart_update_quantity'),
    path('add/<int:item_id>/<int:quantity>/', add_to_cart, name='add_to_cart'),

    path('code/<slug:code>/', apply_code, name='apply_discount_code')
]
