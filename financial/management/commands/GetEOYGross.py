from django.core.management.base import BaseCommand
from moneyed import Money

from checkout.models import Cart
from intake.distributors.utility import log
from intake.models import POLine
from inventory_report.management.commands.GetCogs import get_purchased_as
from partner.models import Partner
from shop.models import InventoryItem


class Command(BaseCommand):
    def handle(self, *args, **options):
        year = 2022
        f = open("reports/eoy_gross.txt", "a")
        gross = Money(0, 'USD')
        shipping = Money(0, 'USD')
        tax = Money(0, 'USD')
        total = Money(0, 'USD')
        for cart in Cart.submitted.filter(status__in=[Cart.PAID, Cart.COMPLETED], date_paid__year=year) \
                .order_by("date_paid"):
            gross += cart.get_total_subtotal()
            gross += cart.final_ship
            shipping += cart.final_ship
            tax += cart.final_tax
            total += cart.final_total
        log(f, "{} was collected gross (net sales tax) in {}".format(gross, year))
        log(f, "{} of that was shipping".format(shipping))
        log(f, "{} was collected in tax ".format(tax))
        log(f, "{} was collected total".format(total))

        partner = Partner.objects.get(name__icontains="CG&T")
        po_lines = POLine.objects.filter(po__partner=partner)

        valhalla_collected = Money("0", 'USD')
        spent_on_sold = Money("0", 'USD')

        for cart in Cart.submitted.filter(status__in=[Cart.PAID, Cart.COMPLETED], date_paid__year=year) \
                .order_by("date_paid"):
            for line in cart.lines.filter(partner_at_time_of_submit=partner):
                valhalla_collected += line.get_subtotal()
                if line.item and line.item.product and line.item.product.barcode:
                    cost = get_purchased_as(0, f, po_lines,
                                            line.item.product.barcode,
                                            line.item.product.name)
                    spent_on_sold += (line.quantity * cost)

        log(f, "Valhalla Collected {} (not including tax or shipping)".format(valhalla_collected))
        log(f, "Valhalla Spent {} on inventory that was sold".format(spent_on_sold))


        remaining_inventory = Money("0", 'USD')

        for item in InventoryItem.objects.filter(partner=partner):
            if item and item.product and item.product.barcode:
                cost = get_purchased_as(0, f, po_lines,
                                        item.product.barcode,
                                        item.product.name)
                remaining_inventory += (item.current_inventory * cost)

        log(f, "Remaining Inventory is approximately {}".format(remaining_inventory))

        log(f, "End of Report\n\n")
        f.close()
