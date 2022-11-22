from django.urls import path
from .views import *
from .models import Cart

urlpatterns = [
    path('', checkout_start, name=Cart.V_START),
    path('login/', checkout_login, name=Cart.V_LOGIN),
    path('pickup_or_ship/', checkout_delivery_method, name=Cart.V_DELIVERY_METHOD),
    path('shipping_addr/', checkout_shipping_address, name=Cart.V_SHIPPING_ADDR),

    path('payment_method/', checkout_payment_method, name=Cart.V_PAYMENT_METHOD),
    path('billing_addr/', checkout_billing_addr, name=Cart.V_BILLING_ADDRESS),
    path('pay_online/', checkout_pay_online, name=Cart.V_PAY_ONLINE),

    path('done/', checkout_done, name=Cart.V_DONE),

    path('create_stripe_payment/', create_stripe_payment, name='create_stripe_payment'),

    path('stripe_webhook/', stripe_webhook),

    path('all_orders_tax/', all_orders_tax, name="all_orders_tax")

]
