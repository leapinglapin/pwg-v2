from django.contrib.sites.models import Site
from django.test import TestCase
from djmoney.money import Money

from checkout.models import Cart, ShippingAddress
from partner.models import Partner
from realaddress.models import RealCountry
from shop.models import Product, InventoryItem


class CheckoutTestCase(TestCase):
    def setUp(self):
        site, _ = Site.objects.get_or_create(name="Test site")
        product, _ = Product.objects.get_or_create(name="Test Product")
        partner, _ = Partner.objects.get_or_create(name="Test Partner")
        item, _ = InventoryItem.objects.get_or_create(product=product, partner=partner, price=Money(5, "USD"),
                                                      default_price=Money(5, "USD"))

        us_country, _ = RealCountry.objects.get_or_create(iso_3166_1_a2="US")

        cart, _ = Cart.objects.get_or_create(site=site, email="Test@comicsgamesandthings.com", status=Cart.OPEN)
        address, _ = ShippingAddress.objects.get_or_create(
            first_name='Albi',
            last_name='Haskell',
            line1='line1',
            line2='line2',
            line4='verona',
            state='WI',
            postcode='53593',
            country=us_country,
        )

        cart.shipping_address = address
        cart.delivery_method = cart.SHIP_ALL
        cart.add(item)
        cart.save()

    def test_pay(self):
        cart = Cart.objects.get(email="Test@comicsgamesandthings.com")
        cart.pay_amount(Money(9.28, "USD"))

        self.assertEqual(cart.final_total, Money("9.28", 'USD'))
        self.assertEqual(cart.final_ship, Money("4.00", 'USD'))
        self.assertEqual(cart.final_tax, Money(".28", 'USD'))
