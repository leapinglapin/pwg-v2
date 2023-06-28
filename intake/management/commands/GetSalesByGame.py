from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand
from moneyed import Money

from checkout.models import Cart, CheckoutLine
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
        po_lines = POLine.objects.filter(po__partner=partner, po__date__year=year)
        cart_lines = CheckoutLine.objects.filter(partner_at_time_of_submit=partner,
                                                 cart__status__in=[Cart.PAID, Cart.COMPLETED],
                                                 cart__date_paid__year=year)
        for game in Game.objects.all().order_by('name'):
            spent_on_game = Money("0", 'USD')
            spent_on_sold_for_game = Money("0", 'USD')
            collected_on_game = Money("0", 'USD')
            log(f, "For {}:".format(game.name))
            for line in cart_lines.filter(item__product__games=game):
                if line.item and line.item.product and line.item.product.barcode:
                    collected_on_game += line.get_subtotal()
                else:
                    log(f, "{} no longer has an item".format(line))
            product_barcodes = Product.objects.filter(games=game).values_list('barcode', flat=True)
            for line in po_lines.filter(barcode__in=product_barcodes):
                try:
                    spent_on_game += (line.actual_cost * line.expected_quantity)
                except Exception:
                    print("Something is wrong with {}".format(line))

            log(f, "{} was collected from customers".format(collected_on_game))
            # log(f, "{} was spent on that inventory, for a margin of {}".format(spent_on_sold_for_game,
            #                                                                    collected_on_game - spent_on_sold_for_game))
            log(f, "{} was spent on that game total, and the difference is {}".format(spent_on_game,
                                                                                      collected_on_game - spent_on_game))

        log(f, "End of report\n\n")
        f.close()
