import csv
import datetime
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from checkout.models import Cart, CheckoutLine
from digitalitems.models import DigitalItem
from partner.models import Partner


class Command(BaseCommand):
    def handle(self, *args, **options):
        partners = list(Partner.objects.all().order_by('id').values_list('name', flat=True))
        print(partners)
        with open('reports/digital_fees_earnings_report{}.csv'.format(datetime.date.today().isoformat()), 'w',
                  newline='') as csvfile:
            fieldnames = ["Year", "Month", "Total"] + partners
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for year in [2020, 2021, 2022]:
                for month in range(1, 13):
                    start = datetime.date(year=year, month=month, day=1)
                    if month != 12:
                        end = datetime.date(year=year, month=month + 1, day=1)
                    else:
                        end = datetime.date(year=year + 1, month=1, day=1)
                    row_info = {}
                    row_info['Year'] = year
                    row_info['Month'] = month
                    sold_items = CheckoutLine.objects.filter(cart__status=Cart.COMPLETED,
                                                             item__polymorphic_ctype=ContentType.objects.get_for_model(
                                                                 DigitalItem),
                                                             cart__date_paid__gte=start, cart__date_paid__lt=end)
                    print(sold_items.count())
                    total_collected = sold_items.aggregate(Sum('price_per_unit_at_submit'))[
                        'price_per_unit_at_submit__sum']
                    print(total_collected)
                    if total_collected:
                        row_info["Total"] = Decimal(.04) * Decimal(total_collected)
                    else:
                        row_info["Total"] = 0

                    for partner in partners:
                        total_collected = sold_items.filter(item__partner__name=partner).aggregate(
                            Sum('price_per_unit_at_submit'))['price_per_unit_at_submit__sum']
                        if total_collected:
                            row_info[partner] = Decimal(.04) * Decimal(total_collected)
                        else:
                            row_info[partner] = 0
                    writer.writerow(row_info)
