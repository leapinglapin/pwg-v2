from django.urls import path

from .api_views import create_paypal_payment, capture_paypal_payment, pay_at_pickup_location, create_stripe_payment, \
    confirm_stripe_capture, payment_api_info
from .models import Cart
from .views import checkout_start, checkout_react, checkout_login, checkout_delivery_method, checkout_shipping_address, \
    checkout_payment_method, checkout_billing_addr, checkout_pay_online, checkout_done, stripe_webhook, all_orders_tax, checkout_complete

urlpatterns = [
    path('', checkout_start, name=Cart.V_START),
    path('v2/', checkout_react, name='checkout_react'),
    path('api/', checkout_react, name='checkout_api_endpoint'),

    path('login/', checkout_login, name=Cart.V_LOGIN),
    path('pickup_or_ship/', checkout_delivery_method, name=Cart.V_DELIVERY_METHOD),
    path('shipping_addr/', checkout_shipping_address, name=Cart.V_SHIPPING_ADDR),

    path('payment_method/', checkout_payment_method, name=Cart.V_PAYMENT_METHOD),
    path('billing_addr/', checkout_billing_addr, name=Cart.V_BILLING_ADDRESS),
    path('pay_online/', checkout_pay_online, name=Cart.V_PAY_ONLINE),

    path('done/', checkout_done, name=Cart.V_DONE),

    path('complete/<order_id>/', checkout_complete, name="checkout_complete"),

    path('confirm_stripe_capture/', confirm_stripe_capture, name="confirm_stripe_capture"),

    path('create_stripe_payment/', create_stripe_payment, name='create_stripe_payment'),
    path('create_paypal_payment/', create_paypal_payment, name='create_paypal_payment'),
    path('capture_paypal_payment/<order_id>/', capture_paypal_payment, name='capture_paypal_payment'),

    path('pay_at_pickup_location/', pay_at_pickup_location, name='pay_at_pickup_location'),

    path('stripe_webhook/', stripe_webhook),

    path('payment_api_info/', payment_api_info),

    path('all_orders_tax/', all_orders_tax, name="all_orders_tax")

]
