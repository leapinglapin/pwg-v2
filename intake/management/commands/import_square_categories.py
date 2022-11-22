from django.core.management.base import BaseCommand, CommandError
from squarelink.squareInterface import SquareInventory
from shop.models import Partner


class Command(BaseCommand):
    help = 'Import categories from Square'

    def handle(self, *args, **options):

        sq = SquareInventory(partner=Partner.objects.filter(hide=False).first())
        cats = sq.get_categories()
        for cat in cats:
            print(cat)
