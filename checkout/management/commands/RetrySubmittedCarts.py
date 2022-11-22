from django.core.management.base import BaseCommand

import traceback

from checkout.models import Cart


class Command(BaseCommand):
    def handle(self, *args, **options):
        for cart in Cart.objects.filter(status__in=[Cart.SUBMITTED, Cart.FROZEN]).order_by('id'):
            if cart.stripepaymentintent_set.exists():
                print("{}: {}".format(cart.id, cart))
            try:
                for intent in cart.stripepaymentintent_set.all():
                    print(intent)
                    intent.captured = False
                    intent.save()  # Reset status of all payment intents that haven't actually through.
                    intent.try_mark_captured()  # Check to see if they now have correct data
            except Exception as e:
                print(e)
                traceback.print_exc()
