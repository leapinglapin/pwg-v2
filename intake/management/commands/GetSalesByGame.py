from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand
from moneyed import Money

from checkout.models import Cart
from game_info.models import Game
from intake.distributors.utility import log
from intake.models import POLine
from inventory_report.management.commands.GetCogs import get_purchased_as
from inventory_report.models import InventoryReport
from partner.models import Partner
from shop.models import Product



class Command(BaseCommand):
    def handle(self, *args, **options):
        year = 2022
        f = open("reports/earnings by game.txt", "a")
        inv_report_lines = InventoryReport.objects.first().report_lines.all()
        partner = Partner.objects.get(name__icontains="CG&T")

        log(f, "End of year Earnings by Game report")
        po_lines = POLine.objects.filter(po__partner=partner)
        for game in Game.objects.all().order_by('name'):
            spent_on_game = Money("0", 'USD')
            spent_on_sold_for_game = Money("0", 'USD')
            collected_on_game = Money("0", 'USD')
            log(f, "For {}:".format(game.name))
            for cart in Cart.submitted.filter(status__in=[Cart.PAID, Cart.COMPLETED], date_paid__year=year) \
                    .order_by("date_paid"):
                for line in cart.lines.filter(partner_at_time_of_submit=partner, item__product__games=game):
                    if line.item and line.item.product and line.item.product.barcode:
                        spent_on_sold_for_game = get_purchased_as(spent_on_sold_for_game, f, po_lines,
                                                                  line.item.product.barcode,
                                                                  line)
                        collected_on_game += line.get_subtotal()
                    else:
                        log(f, "{} no longer has an item".format(line))

            unsold_inventory_cost = Money("0", 'USD')
            for product in Product.objects.filter(games=game):
                for line in POLine.objects.filter(po__date__year=year, po__partner=partner, barcode=product.barcode):
                    if line.actual_cost:
                        spent_on_game += (line.actual_cost * line.received_quantity)
                    for rl in inv_report_lines.filter(barcode=line.barcode):  # Currently, we only have one.
                        unsold_inventory_cost = get_purchased_as(unsold_inventory_cost, f, po_lines, rl.barcode, rl)
                        # Update this to look at a specific inventory report.

            log(f, "{} was collected from customers".format(collected_on_game))
            log(f, "{} was spent on that inventory, for a margin of {}".format(spent_on_sold_for_game,
                                                                               collected_on_game - spent_on_sold_for_game))
            log(f, "{} was spent on that game total, for a margin of {}".format(spent_on_game,
                                                                                collected_on_game - spent_on_game))
            # log(f, "The remaining inventory costs {}".format(unsold_inventory_cost))
            log(f, "Cost of inventory purchased minus remaining inventory (COGS) : {}".format(
                spent_on_game - unsold_inventory_cost))

        log(f, "End of report\n\n")
        f.close()
