import traceback

import pandas
from django.core.management.base import BaseCommand, CommandError

from intake.distributors import alliance, acd, parabellum, vallejo
from intake.models import *
import requests


class Command(BaseCommand):
    help = 'Loops through imported distributor records'

    def add_arguments(self, parser):
        parser.add_argument('partner_slug', type=str)

    def handle(self, *args, **options):

        if options['partner_slug']:
            partner = Partner.objects.get(slug=options['partner_slug'])
            print(partner)
        else:
            print("need partner")
            return

        file = pandas.ExcelFile('./intake/inventories/Master Finances Spreadsheet.xlsx')
        dataframe = pandas.read_excel(file, header=0, sheet_name='Inventory Purchases')

        records = dataframe.astype('string').fillna("").to_dict(orient='records')
        for row in records:
            print(row)
            try:
                distributor = row.get("Distributor")
                number = row.get("Invoice Number")
                date = row.get("Purchase Date")
                subtotal = row.get("Invoice Subtotal")
                fees = row.get("Invoice Shipping+Fees")
                name = row.get("Name of Product")
                barcode = row.get("Barcode")
                quantity = row.get("Quantity")
                line_subtotal = row.get("Subtotal")

                distributor, _ = Distributor.objects.get_or_create(dist_name=distributor)
                distributor.save()
                po, _ = PurchaseOrder.objects.get_or_create(distributor=distributor, po_number=number, partner=partner)
                po.amount_charged = Money(float(subtotal) + float(fees), "USD")
                po.subtotal = subtotal
                po.date = date
                po.save()

                po_line, _ = POLine.objects.get_or_create(name=name, po=po)
                po_line.barcode = barcode
                po_line.expected_quantity = quantity
                po_line.cost_per_item = Money(float(line_subtotal) / float(quantity), "USD")
                po_line.save()

            except Exception as e:
                print(e)
                traceback.print_exc()
                print("Not full line, can't get values; or invalid data")
