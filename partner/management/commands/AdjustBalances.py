from datetime import datetime

from django.core.management.base import BaseCommand

import traceback

from checkout.models import Cart
from partner.models import Partner


class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open("reports/partner_adjustments.txt", "a")
        for partner in Partner.objects.all().order_by('name'):
            log(f, "{} had balance of {} at {}".format(partner.name, partner.acct_balance, datetime.now()))
            partner.reset_balance()
            log(f, 'Reset balance for {}'.format(partner.name))

        for cart in Cart.submitted.all():
            cart.clear_partner_payments()
        for cart in Cart.submitted.all().order_by('date_paid'):
            cart.pay_partners(suppress_emails=True)
        for partner in Partner.objects.all().order_by('name'):
            partner.update_balance()
            log(f, "{} has balance of {} at {}".format(partner.name, partner.acct_balance, datetime.now()))
        f.write("Adjustment complete")
        f.close()


def log(f, string):
    print(string)
    f.write(string + "\n")
