import csv
import datetime
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Sum

from checkout.models import Cart, CheckoutLine
from digitalitems.models import DigitalItem
from partner.models import Partner, PartnerTransaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        partners = list(Partner.objects.all().order_by('id').values_list('name', flat=True))
        print(partners)
        with open('reports/platform_digital_earnings_{}.csv'.format(datetime.date.today().isoformat()), 'w',
                  newline='') as csvfile:
            fieldnames = ["Year", "Month", "Total Sales", "Our Cut on Sales", "Total Patreon Integration Fees"]
            for partner_name in partners:
                fieldnames.append("{} Sales".format(partner_name))
                fieldnames.append("Our cut from {}".format(partner_name))
                fieldnames.append("Patreon fees from {}".format(partner_name))
                fieldnames.append("Payouts fees to {}".format(partner_name))

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
                    sold_items = CheckoutLine.objects.filter(cart__status=Cart.COMPLETED,
                                                             item__polymorphic_ctype=ContentType.objects.get_for_model(
                                                                 DigitalItem),
                                                             cart__date_paid__gte=start, cart__date_paid__lt=end)
                    total_collected = sold_items.aggregate(Sum('price_per_unit_at_submit'))[
                        'price_per_unit_at_submit__sum']
                    row_info["Total Sales"] = total_collected

                    if total_collected:
                        row_info["Our Cut on Sales"] = Decimal(.04) * Decimal(total_collected)
                    else:
                        row_info["Our Cut on Sales"] = 0

                    transactions = PartnerTransaction.objects.filter(is_summary=False, timestamp__gte=start,
                                                                     timestamp__lt=end)
                    row_info['Total Patreon Integration Fees'] = transactions.count() * .10

                    for partner_name in partners:
                        total_collected = sold_items.filter(item__partner__name=partner_name).aggregate(
                            Sum('price_per_unit_at_submit'))['price_per_unit_at_submit__sum']

                        partner_name = partner_name
                        row_info["{} Sales".format(partner_name)] = total_collected
                        if total_collected:
                            row_info["Our cut from {}".format(partner_name)] = Decimal(.04) * Decimal(total_collected)
                        else:
                            row_info["Our cut from {}".format(partner_name)] = 0

                        patreon_fees = transactions.filter(partner__name=partner_name,
                                                           transaction_fees=.10, transaction_subtotal=0).count() * .10
                        row_info["Patreon fees from {}".format(partner_name)] = patreon_fees
                        payouts = transactions.filter(partner__name=partner_name,
                                                      type=PartnerTransaction.PAYMENT) \
                            .aggregate(Sum('transaction_subtotal'))['transaction_subtotal__sum']
                        row_info["Payouts fees to {}".format(partner_name)] = payouts

                    writer.writerow(row_info)
