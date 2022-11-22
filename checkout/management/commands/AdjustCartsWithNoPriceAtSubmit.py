import csv
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from checkout.models import Cart


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('reports/cart_fix_report{}.txt'.format(datetime.date.today().isoformat()), 'a', newline='') as f:
            for cart in Cart.submitted.filter(status__in=[Cart.PAID, Cart.COMPLETED]).order_by('date_paid'):
                updated = False
                with transaction.atomic():
                    for line in cart.lines.filter(price_per_unit_at_submit=None):
                        try:
                            line.price_per_unit_at_submit = line.get_price()
                            line.save()
                            updated = True
                        except Exception:
                            pass
                if updated:
                    log(f, "Cart {} has a new subtotal of {} and was originally charged {}"
                        .format(cart.id,
                                cart.get_total_subtotal(),
                                cart.final_total))


def log(f, string):
    print(string)
    f.write(string + "\n")
