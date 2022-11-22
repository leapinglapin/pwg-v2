import traceback

import requests

from game_info.models import Game
from intake.models import *
import pandas
import xlrd

from shop.models import Product, Publisher, InventoryItem

dist_name = "Para Bellum Wargames"


def import_records():
    distributor = None
    try:
        Distributor.objects.filter(dist_name="Para Bellum").update(dist_name=dist_name)
    except Exception as e:
        print(e)
        exit()
    try:
        Distributor.objects.get_or_create(dist_name=dist_name)[0]
    except Distributor.MultipleObjectsReturned:
        distributors = Distributor.objects.filter(dist_name__icontains="para")
        distributor = distributors.order_by("id").first()
        print(distributor.id)
        for dist in distributors:
            print(dist.id)
            if dist.id != distributor.id:
                for item in PurchaseOrder.objects.filter(distributor=dist).all():
                    print(item)
                    item.distributor = distributor
                    item.save()
                for item in DistItem.objects.filter(distributor=dist).all():
                    print(item)
                    item.distributor = distributor
                    item.save()
                dist.delete()

    distributor = Distributor.objects.get_or_create(dist_name=dist_name)[0]

    publisher, _ = Publisher.objects.get_or_create(name="Para Bellum Wargames")
    tloak, _ = Game.objects.get_or_create(name="Conquest: The Last Argument of Kings")
    fb, _ = Game.objects.get_or_create(name="Conquest: First Blood")

    file = pandas.ExcelFile('./intake/inventories/Para_Bellum_Order_Form_effective_09.07.2022.01.xlsx')
    dataframe = pandas.read_excel(file, header=2, sheet_name='Conquest Products')

    records = dataframe.astype('string').to_dict(orient='records')
    for row in records:
        print(row)
        try:
            description = "{} \n\n {}".format(row.get('Web Extended Descriptions'), row.get('Contents'))
            weight_string = row.get('Weight (Gr/Oz)').split("/")[-1]
            print(weight_string)
            try:
                weight = float(weight_string) / 16
            except Exception:
                weight = None

            name = "Conquest: " + row.get('Product Name - Collaborations')  # Space at end of string is necessary.
            barcode = row.get('Barcode')
            msrp = Money(row.get('MSRP US$'), currency='USD')
            map = Money(row.get('MAPP US$'), currency='USD')
            if barcode and barcode.strip() != '' and name and name.strip() != '':
                DistItem.objects.filter(distributor=distributor, dist_barcode=barcode).delete()
                item, created = DistItem.objects.get_or_create(
                    distributor=distributor,
                    dist_barcode=barcode,
                    dist_number=row.get('SKU #'),
                )
                item.dist_name = name
                item.dist_barcode = barcode
                item.dist_description = description
                item.weight_lbs = weight
                item.msrp = msrp
                item.map = map
                item.save()

                product, created = Product.objects.get_or_create(
                    barcode=barcode,
                    defaults={'all_retail': True,
                              'release_date': datetime.today(),
                              'description': description,
                              'name': name}
                )
                product.name = name
                product.weight = weight
                product.publisher = publisher
                product.msrp = msrp
                product.all_retail = True
                product.games.add(tloak, fb)
                product.save()
                item, created = InventoryItem.objects.get_or_create(partner=Partner.objects.get(name__icontains="CG&T"),
                                                                    product=product, defaults={
                        'price': map, 'default_price': map
                    })
                item.price = msrp * .8
                item.default_price = msrp * .8
                item.save()

        except Exception as e:
            traceback.print_exc()
            print("Not full line, can't get values")
