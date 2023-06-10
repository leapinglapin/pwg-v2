import datetime

import stripe
from django.core.management.base import BaseCommand

import traceback

from checkout.models import Cart


class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open("reports/fixed_cart_dates.txt", "a")

        for cart in Cart.objects.filter(status__in=[Cart.COMPLETED]).order_by('id'):
            print("{}: {}".format(cart.id, cart))
            try:
                for intent in cart.stripepaymentintent_set.all():
                    print(intent)
                    si = stripe.PaymentIntent.retrieve(intent.id)
                    cart = intent.cart
                    original_date_paid = cart.date_paid
                    if si.amount_received > 0:
                        timestamp = si.charges.data[0].created
                        cart.date_paid = datetime.datetime.fromtimestamp(timestamp)
                        cart.save()
                        if original_date_paid != cart.date_paid:
                            log(f, "{}'s date was changed from {} to {}".format(
                                cart.id, original_date_paid, cart.date_paid
                            ))
            except Exception as e:
                print(e)
                traceback.print_exc()
        f.close()


def log(f, string):
    print(string)
    f.write(string + "\n")
