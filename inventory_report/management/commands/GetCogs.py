from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand
from moneyed import Money

from checkout.models import Cart
from intake.models import PurchaseOrder, POLine
from inventory_report.models import InventoryReport
from partner.models import Partner


def get_purchased_as(cost_counter, logfile, po_lines, barcode, name):
    purchased_as_options = po_lines.filter(barcode=barcode)
    if purchased_as_options.exists():
        p_as = purchased_as_options.order_by('po__date').first()
        if p_as.actual_cost:
            cost_counter += p_as.actual_cost
        else:
            pass
            # log(logfile, "{} does not have an actual cost in poline {}".format(name, p_as))

    else:
        pass
        # log(logfile, "{} does not exist in a purchase order".format(name))
    return cost_counter


class Command(BaseCommand):
    def handle(self, *args, **options):
        year = 2021
        f = open("reports/cogs.txt", "a")
        partner = Partner.objects.get(name__icontains="CG&T")

        log(f, "End of year Cost of Goods Sold Report")
        po_lines = POLine.objects.filter(po__partner=partner)

        total_inventory_purchased = Money("0", 'USD')
        for po in PurchaseOrder.objects.filter(date__year=year, partner=partner):
            for line in po.lines.all():
                if line.actual_cost:
                    total_inventory_purchased += (line.actual_cost * line.received_quantity)
        log(f, "{} of inventory was purchased in {}".format(total_inventory_purchased, year))

        cost_of_goods_sold = Money("0", 'USD')
        for cart in Cart.submitted.filter(status__in=[Cart.PAID, Cart.COMPLETED], date_paid__year=year) \
                .order_by("date_paid"):
            for line in cart.lines.filter(partner_at_time_of_submit=partner):
                if line.item and line.item.product and line.item.product:
                    cost_of_goods_sold = get_purchased_as(cost_of_goods_sold, f, po_lines, line.item.product.barcode,
                                                          line)
                else:
                    log(f, "{} no longer has an item".format(line))

        log(f, "The total cost of goods sold is {} (Not actual cost per item, need to do that)"
            .format(cost_of_goods_sold))

        unsold_inventory_cost = Money("0", 'USD')
        for line in InventoryReport.objects.first().report_lines.all():  # Currently, we only have one.
            unsold_inventory_cost = get_purchased_as(unsold_inventory_cost, f, po_lines, line.barcode, line)
        log(f, "The remaining inventory costs {} (Not actual cost per item, need to do that)"
            .format(unsold_inventory_cost))
        log(f, "Cost of inventory purchased minus cost of goods sold (Theoretically equal to above?) : {}".format(
            total_inventory_purchased - cost_of_goods_sold))
        log(f, "Cost of inventory purchased minus remaining inventory (COGS) : {}".format(
            total_inventory_purchased - unsold_inventory_cost))
        log(f, "End of report\n\n")
        f.close()


def log(f, string):
    print(string)
    f.write(string + "\n")
