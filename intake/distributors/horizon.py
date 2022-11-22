from django.core.management.base import BaseCommand, CommandError

from intake.upcbar import upcbar
from intake.models import DistItem, Distributor, Manufacturer, ManufacturerAbbreviation, ManufacturerBarcode
import csv
dist_name = "Horizon"

def import_records(self, file):
    distributor = Distributor.objects.get_or_create(dist_name=dist_name)[0]
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if len(row) == 0:
                pass
            else:

                print(f'\t{row[0]} is the {row[1]}, and costs {row[3]}.')
                # print(row)
                available = 0
                i = 0
                if i in range(7, 11):
                    available |= row[i]


                item = DistItem.objects.get_or_create(distributor=distributor, dist_number=row[0])[0]
                item.dist_name = row[1]
                item.msrp = float(row[3])
                item.map = float(row[4])
                item.dist_price = float(row[15])
                if available == 0:
                    item.dist_availability = 'YES'
                else:
                    item.dist_availability = 'NO'
                item.dist_barcode = row[2]
                abrv = row[10]

                barcode_segment = upcbar(item.dist_barcode).get_prefix()
                mfc, created = Manufacturer.objects.get_or_create(
                    manufacturerabbreviation__abbreviation=abrv,
                    manufacturerabbreviation__distributor=distributor)
                if created:
                    mfc.mfc_name = abrv
                    mfc.save()
                    # print(mfc, distributor, abrv)
                    mfc_abrv, c2 = ManufacturerAbbreviation.objects.get_or_create(mfc=mfc,
                                                                                  distributor=distributor,
                                                                                  abbreviation=abrv)
                    mfc_abrv.save()
                    if barcode_segment:
                        if not abrv:
                            mfc.mfc_name = barcode_segment
                        # print("Barcode Segment:", mfc, barcode_segment)
                        mfc_brcd, c3 = ManufacturerBarcode.objects.get_or_create(mfc=mfc,
                                                                                 barcode_prefix=barcode_segment)
                        mfc_brcd.save()
                else:
                    item.manufacturer = mfc

                item.save()

            line_count += 1
        print(f'Processed {line_count} lines.')
