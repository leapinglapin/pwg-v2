import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from intake.models import TradeRange
from partner.models import Partner
from shop.models import InventoryItem


class Command(BaseCommand):

    def handle(self, *args, **options):
        f = open("reports/trade range inventory report.txt", "a")
        for tr in TradeRange.objects.all():
            if tr.name != "nan":
                log(f, "\nTR {} {} as of {}".format(tr.distributor, tr.name, datetime.now()))

                for di in tr.contains.all():
                    if di.quantity_per_pack == 1:
                        try:
                            item = InventoryItem.objects.get(partner=Partner.objects.get(name__icontains="CG&T"),
                                                             product__barcode=di.dist_barcode)
                            if item.current_inventory == 0:
                                log(f, "CG&T is out of {}".format(item))
                        except InventoryItem.DoesNotExist:
                            log(f, "CG&T does not carry {}".format(item))


def log(f, string):
    print(string)
    f.write(string + "\n")
