import csv
import datetime

from django.core.management import BaseCommand
from djmoney.money import Money

from billing.models import BillingEvent
from partner.models import PartnerTransaction, Partner


class Command(BaseCommand):
    def handle(self, *args, **options):
        partners = list(Partner.objects.all().order_by('id').values_list('name', flat=True))
        # print(partners)
        with open('reports/platform_charges_{}.csv'.format(datetime.date.today().isoformat()), 'w',
                  newline='') as csvfile:
            fieldnames = ["Year", "Month", "Partner Transactions", "Integration Charges"]
            for partner_name in partners:
                fieldnames.append("{} (old)".format(partner_name))
                fieldnames.append("{} (new)".format(partner_name))

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
                    partner_transactions = PartnerTransaction.objects.filter(timestamp__gte=start, timestamp__lt=end,
                                                                             transaction_fees=Money('.10', "USD"))
                    transactions_total_amount = partner_transactions.count() * Money(.10, "USD")
                    row_info["Partner Transactions"] = transactions_total_amount

                    integration_charges = BillingEvent.objects.filter(timestamp__gte=start, timestamp__lt=end,
                                                                      type=BillingEvent.INTEGRATION_CHARGE)
                    integrations_total_amount = integration_charges.count() * Money(.10, "USD")
                    row_info["Integration Charges"] = integrations_total_amount

                    difference = integrations_total_amount - transactions_total_amount

                    change = "Infinite"
                    if transactions_total_amount > Money(0, "USD"):
                        change = -(1 - (integrations_total_amount / transactions_total_amount)) * 100

                    print("Old: {}, New: {}, Difference {}, or {}%".format(transactions_total_amount,
                                                                           integrations_total_amount,
                                                                           difference, change
                                                                           ))

                    for partner_name in partners:
                        partner_transactions = PartnerTransaction.objects.filter(timestamp__gte=start,
                                                                                 timestamp__lt=end,
                                                                                 partner__name=partner_name,
                                                                                 transaction_fees=Money('.10', "USD"))
                        transactions_total_amount = partner_transactions.count() * Money(.10, "USD")
                        row_info["{} (old)".format(partner_name)] = transactions_total_amount

                        integration_charges = BillingEvent.objects.filter(timestamp__gte=start, timestamp__lt=end,
                                                                          partner__name=partner_name,
                                                                          type=BillingEvent.INTEGRATION_CHARGE)
                        integrations_total_amount = integration_charges.count() * Money(.10, "USD")
                        row_info["{} (new)".format(partner_name)] = integrations_total_amount

                    writer.writerow(row_info)

        fieldnames = ["Partner", "Partner Transaction ID",
                      "Pledge ID", "Pledge timestamp", "Email", "User",
                      "Created Timestamp"]
        csvfile = open("reports/non-migrated pt charges.csv", "w")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pt in PartnerTransaction.objects.filter(transaction_fees=Money(.10, "USD"), is_summary=False,
                                                    migrated_to__isnull=True):
            row_info = {
                "Partner": pt.partner.name,
                "Partner Transaction ID": pt.id,
                "Created Timestamp": pt.created_timestamp,
            }
            if pt.linked_pledge.exists():
                linked_pledge = pt.linked_pledge.first()
                row_info.update({
                    "Pledge ID": linked_pledge.id,
                    "Pledge timestamp": linked_pledge.date,
                    "Email": linked_pledge.email,
                    "User": linked_pledge.user,
                })
            writer.writerow(row_info)
