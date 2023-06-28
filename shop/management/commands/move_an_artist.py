from django.apps import apps
from django.core.management.base import BaseCommand
from polymorphic.utils import reset_polymorphic_ctype

from partner.models import Partner
from shop.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_partner = Partner.objects.get(name="LeesedRenfort")
        with open('list.txt') as f:
            for line in f.readlines():
                line = line.strip()
                print(line)
                try:
                    product = Product.objects.get(slug=line)
                    product.partner = new_partner
                    product.save()
                    for item in product.item_set.all():
                        pass
                        item.partner = new_partner
                        item.save()
                except Exception:
                    print("Product {} Does Not Exist".format(line))


