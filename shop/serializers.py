from rest_framework import serializers

from digitalitems.models import DigitalItem
from partner.serializers import PartnerSerializer
from .models import Item, Product, InventoryItem, MadeToOrder


class ProductSerializer(serializers.ModelSerializer):
    visible = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'visible')

    @staticmethod
    def get_visible(product):
        return product.visible


class ItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    type = serializers.SerializerMethodField()
    partner = PartnerSerializer()
    backorders_enabled = serializers.SerializerMethodField()
    inventory = serializers.SerializerMethodField()
    is_preorder = serializers.SerializerMethodField()
    is_pay_what_you_want = serializers.SerializerMethodField()
    button_status = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            'id', 'type', 'product', 'price', 'default_price', 'partner', 'inventory',
            'backorders_enabled', 'is_preorder', 'button_status', 'is_pay_what_you_want',
        )

    @staticmethod
    def get_type(item):
        return item.get_type()

    @staticmethod
    def get_inventory(item):
        if isinstance(item, InventoryItem) or isinstance(item, MadeToOrder):
            return item.get_inventory()
        else:
            return 0

    @staticmethod
    def get_is_pay_what_you_want(item):
        if isinstance(item, DigitalItem):
            return item.pay_what_you_want
        else:
            return False

    @staticmethod
    def get_backorders_enabled(item):
        if isinstance(item, InventoryItem):
            return item.allow_backorders
        elif isinstance(item, MadeToOrder):
            return True
        else:
            return False

    @staticmethod
    def get_is_preorder(item):
        return item.product.is_preorder

    def get_button_status(self, item):
        cart = self.context.get("cart")
        text, enabled = item.button_status(cart=cart)
        return {'text': text, 'enabled': enabled}
