import psycopg as psycopg
from django.core.management.base import BaseCommand
from django.db import connection

from checkout.models import CheckoutLine
from discount_codes.models import Referrer
from giveaway.models import Giveaway
from images.models import Image
from partner.models import Partner
from shop.models import Item, Product, ProductImage


class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as dest_curr:

            for referrer in Referrer.objects.all():
                referrer.referrer_is_partner = None
                referrer.save()

            for partner in Partner.objects.exclude(name="Valhalla Hobby: CG&T Verona"):
                print(partner)
                ProductImage.objects.filter(partner=partner.id).delete()
                ProductImage.objects.filter(item__partner=partner.id).delete()
                ProductImage.objects.filter(product__partner=partner.id).delete()
                ProductImage.objects.filter(partner_images__partner=partner.id).delete()

                Image.objects.filter(partner=partner).delete()
                Image.objects.filter(products__partner=partner).delete()


                CheckoutLine.objects.filter(partner_at_time_of_submit=partner).delete()
                CheckoutLine.objects.filter(item__partner=partner).delete()



                # We cannot use the standard delete method because there are items in the system that do not have an object.
                dest_curr.execute("""DELETE FROM shop_item where "partner_id"={}""".format(partner.id))

                dest_curr.execute("""DELETE FROM shop_product_categories where product_id in (select id from shop_product where "partner_id"={})""".format(partner.id))
                dest_curr.execute("""DELETE FROM shop_product_games where product_id in (select id from shop_product where "partner_id"={})""".format(partner.id))
                dest_curr.execute("""DELETE FROM shop_product_editions where product_id in (select id from shop_product where "partner_id"={})""".format(partner.id))
                dest_curr.execute("""DELETE FROM shop_product_factions where product_id in (select id from shop_product where "partner_id"={})""".format(partner.id))

                Giveaway.objects.filter(product__partner=partner).delete()

                dest_curr.execute("""DELETE FROM shop_product where "partner_id"={}""".format(partner.id))

                #partner.image_set.all().delete()
                #partner.administrators.clear()
                dest_curr.execute("""DELETE FROM partner_partner where "id"={}""".format(partner.id))
                partner.delete()

                # Product.objects.filter(partner=partner).delete()
                # partner.delete()
