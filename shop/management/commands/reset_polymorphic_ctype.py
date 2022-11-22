from django.apps import apps
from django.core.management.base import BaseCommand
from polymorphic.utils import reset_polymorphic_ctype


class Command(BaseCommand):
    def handle(self, *args, **options):
        Item = apps.get_model('shop', 'Item')
        InventoryItem = apps.get_model('shop', 'InventoryItem')
        DigitalItem = apps.get_model('digitalitems', 'DigitalItem')
        ContentType = apps.get_model('contenttypes', 'ContentType')


        reset_polymorphic_ctype(Item, DigitalItem, InventoryItem)
