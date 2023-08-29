import traceback

import requests

from game_info.models import Game
from intake.models import *
import pandas
import xlrd

from shop.models import Product, Publisher, InventoryItem

dist_name = "Wyrd Miniatures"


def import_records():
    distributor = Distributor.objects.get_or_create(dist_name=dist_name)[0]

    publisher, _ = Publisher.objects.get_or_create(name=dist_name)

    pricelist = pandas.ExcelFile('./intake/inventories/02.22.PRICELIST.xlsx')
    dataframe = pandas.read_excel(pricelist, header=0, sheet_name='02.22', converters={'UPC': str})
    original_prices = dataframe.to_dict(orient='records')
    for row in original_prices:
        print(row)
        try:
            long_name = row.get("LONG DESCRIPTION")
            name = row.get('SHORT DESCRIPTION')
            barcode = row.get('UPC')
            item_num = row.get('Item')
            msrp = Money(row.get('Price'),
                         currency='USD')  # Not used here, because we set it in from the price increase seheet
            if barcode and barcode.strip() != '' and long_name and long_name.strip() != '':
                DistItem.objects.filter(distributor=distributor, dist_barcode=barcode).delete()
                DistItem.objects.filter(distributor=distributor, dist_number=item_num).delete()
                ditem, created = DistItem.objects.get_or_create(
                    distributor=distributor,
                    dist_number=item_num,
                    dist_barcode=barcode,
                    dist_name=long_name,
                )
                ditem.save()
        except Exception as e:
            traceback.print_exc()
            print("Not full line, can't get values")
    increases = pandas.ExcelFile('./intake/inventories/2022.PRICEINCREASE.xlsx')
    dataframe = pandas.read_excel(increases, header=1, sheet_name='02.22')

    records = dataframe.to_dict(orient='records')
    for row in records:
        print(row)
        try:
            msrp = Money(row.get("Price \nEffective 3/1/22"), currency='USD')
            dist_number = row.get('Item')
            if dist_number:
                ditem = DistItem.objects.get(
                    distributor=distributor,
                    dist_number=dist_number,
                )
                ditem.msrp = msrp
                ditem.save()
        except Exception as e:
            traceback.print_exc()
            print("Not full line, can't get values")

    f = open("reports/products_with_price_adjustments.txt", "a")
    log(f, "Price adjustments for Wyrd 2022")
    for ditem in DistItem.objects.filter(distributor=distributor, dist_barcode__isnull=False):
        print(ditem)
        msrp = ditem.msrp

        try:
            product = Product.objects.get(
                barcode=ditem.dist_barcode,
            )
            product.msrp = msrp
            product.save()

            item, created = InventoryItem.objects.get_or_create(partner=Partner.objects.get(name__icontains="PWG"),
                                                                product=product, defaults={
                    'price': msrp * .8, 'default_price': msrp * .8
                })
            old_price = item.price
            item.price = msrp * .8
            item.default_price = msrp * .8
            item.save()
            if old_price != item.price:
                log(f, "Price for {} updated to {}".format(item, item.price))
                log(f, "\n")

        except Exception as e:
            print("Could not update price for {}".format(ditem))
            print(e)
            traceback.print_exc()

    log(f, "End of Price adjustments for Wyrd 2022")
    f.close()


def log(f, string):
    print(string)
    f.write(string + "\n")
