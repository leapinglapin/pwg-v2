import traceback

import checkdigit.upc
import requests
from checkdigit import gs1

from game_info.models import Game
from intake.models import *
import pandas
import xlrd

from shop.models import Product, Publisher, InventoryItem


def import_records():
    publisher, _ = Publisher.objects.get_or_create(name="Acrylicos Vallejo")

    file = pandas.ExcelFile('./intake/inventories/Paints.xlsx')
    dataframe = pandas.read_excel(file, header=0, sheet_name='Vallejo')

    records = dataframe.astype('string').fillna("").to_dict(orient='records')
    for row in records:
        print(row)
        try:
            description = "{} {}".format(row.get('Web Extended Descriptions'), row.get('Contents'))

            line = row.get("Line")
            subline = row.get("Subline")
            number = row.get("Number")
            if len(number) > 6:
                number = number[:6]
            if len(number) < 5:
                number = number.ljust(5, '0')

            paint_name = row.get("Name")
            size = row.get("Size (ml)")

            if subline and subline.strip() != "":
                name = "Vallejo {} {}: {}: {} {}ml".format(number, line, subline, paint_name, size)
            else:
                name = "Vallejo {} {}: {} {}ml".format(number, line, paint_name, size)

            barcode_start = "8429551" + number.replace('.', '')
            last_digit = gs1.calculate(barcode_start)
            barcode = barcode_start + last_digit
            msrp = row.get('MSRP')
            print("{} {}".format(name, barcode))
            if barcode and barcode.strip() != '' and name and name.strip() != '':
                product, created = Product.objects.get_or_create(
                    all_retail=True,
                    release_date=datetime.today(),
                    barcode=barcode,
                    name=name,
                    publisher=publisher,
                    msrp=msrp,
                    description=description
                )
                product.save()

        except Exception as e:
            traceback.print_exc()
            print("Not full line, can't get values; or invalid data")
