import requests

from intake.models import *
import csv

dist_name = "Alliance"


def import_records(dist_inv_file):
    with requests.get(dist_inv_file.file.url) as r:
        file = r.content
        filename = dist_inv_file.file.name.split('/')[-1]
        distributor = Distributor.objects.get_or_create(dist_name=dist_name)[0]
        # Generate a list of warehouses
        warehouses = {"avail_east": DistributorWarehouse.objects.get_or_create(distributor=distributor,
                                                                               warehouse_name="East - Baltimore"),
                      "avail_midwest": DistributorWarehouse.objects.get_or_create(distributor=distributor,
                                                                                  warehouse_name="Midwest - Fort Wayne, IN"),
                      "avail_southwest": DistributorWarehouse.objects.get_or_create(distributor=distributor,
                                                                                    warehouse_name="Southwest - Austin, TX"),
                      "avail_west": DistributorWarehouse.objects.get_or_create(distributor=distributor,
                                                                               warehouse_name="West - California")}

        csv_reader = csv.reader(file.decode().splitlines(), delimiter='\t')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
            elif len(row) == 0:
                pass
            else:
                print(f'\t{row[0]} is the {row[1]}, and costs {row[2]}.')

                dist_number = row[0]
                dist_item_name = row[1]
                msrp = row[2]
                dist_barcode = None
                # Row 14, 15, or 16 may contain the barcode
                # print(row[14], row[15], row[16])
                if validate_barcode(row[14]):
                    dist_barcode = row[14]
                elif validate_barcode(row[15]):
                    dist_barcode = row[15]
                elif validate_barcode(row[16]):
                    dist_barcode = row[16]

                item, created = DistItem.objects.get_or_create(distributor=distributor, dist_number=dist_number,
                                                               msrp=msrp, dist_name=dist_item_name,
                                                               dist_barcode=dist_barcode)
                item.save()


                dist_inv_file.set_availability(item, warehouses['avail_east'], row[7])
                dist_inv_file.set_availability(item, warehouses['avail_midwest'], row[8])
                dist_inv_file.set_availability(item, warehouses['avail_southwest'], row[9])
                dist_inv_file.set_availability(item, warehouses['avail_west'], row[10])
            line_count += 1
        print(f'Processed {line_count} lines.')


def validate_barcode(barcode):
    if len(barcode) < 12 or len(barcode) > 14:
        return False
    return True


