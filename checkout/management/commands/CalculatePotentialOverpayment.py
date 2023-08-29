import csv

from django.core.management import BaseCommand
from django.db.models import F
from moneyed import Money

from checkout.models import CheckoutLine, Cart
from partner.models import Partner

"""
This file is for calculating overpayment of partner balances where the product may have been linked to the incorrect partner
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        lines = CheckoutLine.objects.filter(partner_at_time_of_submit__isnull=False). \
            exclude(partner_at_time_of_submit=F("item__partner"))
        print(lines.count())
        affected_partner_ids = lines.values_list('item__partner', flat=True).distinct()
        partners = Partner.objects.filter(id__in=affected_partner_ids)
        fieldnames = ["Partner", "Date Paid", "Cart ID", "Status", "User", "Products", "Subtotal",
                      "Fees", "Total"]
        csvfile = open("reports/potential_partner_overpayments.csv", "w")

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for partner in partners:
            print(partner)
            cart_ids = lines.filter(item__partner=partner).values_list("cart__id", flat=True).distinct()
            carts = Cart.submitted.filter(id__in=cart_ids)
            print(carts.count())
            potential_overpay_amount = Money(0, "USD")
            for cart in carts.order_by('date_paid'):
                partner_subtotal = Money(0, "USD")
                partner_fees = Money(0, "USD")
                product_string = ""
                # Assumes that fees would be based on the number of partners at time of submit
                _, number_of_partners = cart.get_order_partners()
                for line in cart.lines.filter(item__partner=partner):
                    if product_string != "":
                        product_string += ", "  # add a comma between product names
                    line_subtotal = line.get_subtotal()
                    partner_subtotal += line_subtotal
                    partner_fees += (line_subtotal * (1 - partner.get_cut(line.item)))
                    if line.name_of_item:
                        product_string += str(line.name_of_item)
                    else:
                        product_string += line.item.product.name

                if number_of_partners > 0:
                    partner_fees += (partner_subtotal * float(.03)) + (Money(.50, 'USD') / number_of_partners)
                potential_overpay_amount += partner_subtotal - partner_fees
                print("Cart {} subtotal was {} and fees were {} for a total of {}". \
                      format(cart.id, partner_subtotal, partner_fees,
                             partner_subtotal - partner_fees))
                writer.writerow({
                    "Partner": partner,
                    "Date Paid": cart.date_paid,
                    "Cart ID": cart.id,
                    "User": cart.owner,
                    "Status": cart.status,
                    "Products": product_string,
                    "Subtotal": partner_subtotal.amount,
                    "Fees": partner_fees.amount,
                    "Total": (partner_subtotal - partner_fees).amount
                })
            print("Potentially overpaid {} by {}".format(partner, potential_overpay_amount))
