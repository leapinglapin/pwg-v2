import csv
import datetime
from _decimal import Decimal

import humanize
from django.core.management.base import BaseCommand
from django.db.models import Sum

from digitalitems.models import DownloadHistory
from partner.models import Partner

TWOPLACES = Decimal('0.01')


class Command(BaseCommand):
    def handle(self, *args, **options):
        partners = list(Partner.objects.all().order_by('id').values_list('name', flat=True))
        print(partners)
        # Round to two places
        with open('reports/platform_bandwidth_usage_{}.csv'.format(datetime.date.today().isoformat()), 'w',
                  newline='') as csvfile:
            fieldnames = ["Year", "Month", "Total Bandwidth"]
            for partner_name in partners:
                fieldnames.append("{}'s Bandwidth (total)".format(partner_name))
                fieldnames.append("{}'s Bandwidth (%)".format(partner_name))

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for year in range(2020, datetime.date.today().year + 1):
                for month in range(1, 13):
                    print("{}/{}".format(year, month))
                    start = datetime.date(year=year, month=month, day=1)
                    if month != 12:
                        end = datetime.date(year=year, month=month + 1, day=1)
                    else:
                        end = datetime.date(year=year + 1, month=1, day=1)
                    row_info = {}
                    row_info['Year'] = year
                    row_info['Month'] = month
                    download_records = DownloadHistory.objects.filter(timestamp__gte=start, timestamp__lt=end)
                    total_bandwidth = download_records.aggregate(Sum('file__file_size'))[
                        'file__file_size__sum']
                    if total_bandwidth:
                        row_info["Total Bandwidth"] = humanize.naturalsize(total_bandwidth)

                        for partner_name in partners:
                            partner_bandwidth = download_records.filter(file__partner__name=partner_name) \
                                .aggregate(Sum('file__file_size'))[
                                'file__file_size__sum']
                            if partner_bandwidth:
                                row_info["{}'s Bandwidth (total)".format(partner_name)] = humanize.naturalsize(
                                    partner_bandwidth)
                                row_info["{}'s Bandwidth (%)".format(partner_name)] = (Decimal(
                                    partner_bandwidth) / Decimal(total_bandwidth)).quantize(TWOPLACES)
                    writer.writerow(row_info)
