import csv

from django.core.management import BaseCommand
from tqdm import tqdm

from checkout.models import Cart
from partner.models import PartnerTransaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        fieldnames = ["Timestamp", "Type",
                      "Customer", "Linked Cart", "Total", "Subtotal", "Fees", "Net",
                      "Balance", "Created Timestamp"]
        csvfile = open("reports/landon_charges.csv", "w")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        all_pts = PartnerTransaction.objects.filter(is_summary=False, partner__slug="leesedrenfort")
        pbar = tqdm(total=all_pts.count(), unit="records")
        for pt in all_pts:
            pbar.update(1)
            cart = Cart.objects.filter(partner_transactions=pt).first()
            row_info = {
                "Created Timestamp": pt.created_timestamp,
                "Timestamp": pt.timestamp,
                "Type": pt.type,
                "Total": pt.transaction_total.amount,
                "Subtotal": pt.transaction_subtotal.amount,
                "Fees": pt.transaction_fees.amount,
                "Net": pt.partner_cut.amount,
                "Balance": pt.balance_after_apply,
            }
            if cart:
                row_info["Linked Cart"]: cart.id
                row_info["Customer"] = cart.owner
            writer.writerow(row_info)
