import csv
import datetime

from django.core.management.base import BaseCommand, CommandError

from checkout.models import Cart
from partner.models import Partner, PartnerTransaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        partners = list(Partner.objects.all().order_by('id').values_list('name', flat=True))
        print(partners)
        with open('reports/integration_charge_earnings_report{}.csv'.format(datetime.date.today().isoformat()), 'w',
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
                    transactions = PartnerTransaction.objects.filter(transaction_fees=.10, transaction_subtotal=0,
                                                                     is_summary=False, timestamp__gte=start,
                                                                     timestamp__lt=end)
                    row_info['Total'] = transactions.count()
                    for partner in partners:
                        row_info[partner] = transactions.filter(partner__name=partner).count()
                    writer.writerow(row_info)
