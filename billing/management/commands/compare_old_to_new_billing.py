import csv

from django.core.management import BaseCommand
from tqdm import tqdm

from partner.models import PartnerTransaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        fieldnames = ["Partner", "Partner Transaction ID", "Type", "Amount",
                      "Pledge ID", "Pledge timestamp", "Email", "User",
                      "Created Timestamp"]
        csvfile = open("reports/non-migrated pt charges.csv", "w")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        nonmigrated = PartnerTransaction.objects.filter(migrated_to__isnull=True, is_summary=False)
        pbar = tqdm(total=nonmigrated.count(), unit="records")
        for pt in nonmigrated:
            pbar.update(1)
            row_info = {
                "Partner": pt.partner.name,
                "Partner Transaction ID": pt.id,
                "Created Timestamp": pt.created_timestamp,
                "Type": pt.type,
                "Amount": pt.partner_cut,
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
