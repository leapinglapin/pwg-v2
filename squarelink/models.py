import datetime
from django.db import models
from djmoney.money import Money
import rfc3339
from square.client import Client

from partner.models import Partner
from shop.models import InventoryItem, Product


class SquareLink(models.Model):
    square_aid = models.CharField(max_length=200)
    square_token = models.CharField(max_length=200)
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE, null=True, unique=True)

    connected = False
    cat_api = None
    inv_api = None
    location_id = None
    tax = None

    def connect(self):
        if self.connected:
            return True
        try:
            # Create an instance of the API Client
            # and initialize it with the credentials
            # for the Square account whose assets you want to manage
            client = Client(
                access_token=self.square_token,
                environment='production',
            )
            # Get an instance of the Square API you want call
            self.cat_api = client.catalog
            self.inv_api = client.inventory

            result = client.locations.list_locations()

            if result.is_success():
                self.location_id = result.body['locations'][0]['id']
                result = self.cat_api.list_catalog(types="TAX")
                if result.is_success():
                    self.tax = result.body['objects'][0]['id']
                self.connected = True
                return True
            elif result.is_error():
                print(result.errors)
                return False
        except SquareLink.DoesNotExist as e:
            print(e)
            print("No API KEY SET FOR SQUARE")
            return False

    def get_categories(self):
        result = self.cat_api.list_catalog(types='CATEGORY')
        namelist = []
        if result.is_success():
            print(result.body)
            categories = result.body['objects'][1:]
            for category in categories:
                name = category['category_data']['name']
                namelist.append(name)
                id = category['id']
                cat, created = SquareCategory.objects.get_or_create(sq_cat_name=name, square_id=id)
                cat.save()
        elif result.is_error():
            print(result.errors)
        return namelist

    def import_all(self):
        if self.connected is False:
            self.connect()
        cursor = ""
        items = 0
        pages = 0
        while True:
            result = self.cat_api.list_catalog(types='ITEM', cursor=cursor)
            if result.is_success():
                pages += 1
                for item_dict in result.body['objects']:
                    try:
                        SquareInventoryItem.from_api_dict(sq_inv=self, api_dict=item_dict)
                        items += 1
                    except ValueError as e:
                        print(e)
                        print("{} items on {} pages".format(items, pages))
                    except Exception as e:
                        print(e)
                        print("issues with {}".format(item_dict))
                        print("{} items on {} pages".format(items, pages))
                    print("{} items on {} pages".format(items, pages), end="\r", flush=True)
                try:
                    cursor = result.body['cursor']
                except KeyError:
                    print("\n")
                    break  # End of paged data
            elif result.is_error():
                print(result.errors)
                break

        print("{} items on {} pages".format(items, pages), end="\r", flush=True)

    def get_item_from_barcode(self, barcode):
        if self.connected is False:
            self.connect()
        body = {}
        body['object_types'] = ['ITEM_VARIATION']
        body['query'] = {}
        body['query']['exact_query'] = {}
        body['query']['exact_query']['attribute_name'] = 'sku'
        body['query']['exact_query']['attribute_value'] = barcode
        result = self.cat_api.search_catalog_objects(body)
        # Call the success method to see if the call succeeded
        if result.is_success():
            # The body property is a list of locations

            try:
                return SquareInventoryItem.from_api_dict(sq_inv=self, api_dict=result.body['objects'][0])
            except ValueError as e:
                print(e)
            except Exception as e:
                print(e)
                print("issues with {}".format(result.body))

        # Call the error method to see if the call failed
        elif result.is_error():
            print('Error calling item api')
            errors = result.errors
            # An error is returned as a list of errors
            for error in errors:
                # Each error is represented as a dictionary
                for key, value in error.items():
                    print(f"{key} : {value}")
                print("\n")

    def get_item_quantity(self, item):
        if self.connected is False:
            self.connect()
        result = self.inv_api.retrieve_inventory_count(item.variation_id)

        if result.is_success():
            print(result.body)
            try:
                return result.body['counts'][0]['quantity']
            except Exception as e:  # Not present
                print(e)
                return 0
                # TODO: Narrow down this exception and verify this is correct behavior
                # and only when the inventory is 0
        elif result.is_error():
            print("Error calling inventory API")
            print(result.errors)

    def add_square_stock(self, item, quantity):
        if self.connected is False:
            self.connect()
        body = {}
        body['idempotency_key'] = rfc3339.rfc3339(datetime.datetime.utcnow())
        body['changes'] = []
        change = {}
        change['type'] = "ADJUSTMENT"
        change['adjustment'] = {}
        change['adjustment']['location_id'] = self.location_id
        change['adjustment']['catalog_object_id'] = item.variation_id
        change['adjustment']['occurred_at'] = rfc3339.rfc3339(datetime.datetime.utcnow())
        change['adjustment']['from_state'] = "NONE"
        change['adjustment']['to_state'] = "IN_STOCK"
        change['adjustment']['quantity'] = str(quantity)
        body['changes'].append(change)
        print(body)
        result = self.inv_api.batch_change_inventory(body)
        if result.is_success():
            print(result.body)
            return result.body['counts'][0]['quantity']
        elif result.is_error():
            print('Error calling item api')
            errors = result.errors
            # An error is returned as a list of errors
            for error in errors:
                # Each error is represented as a dictionary
                for key, value in error.items():
                    print(f"{key} : {value}")
                print("\n")

    def add_new_square_item(self, name, price, category, sku):
        if self.connected is False:
            self.connect()
        try:
            if self.get_item_from_barcode(sku).exists:
                return False
        except Exception:
            return False
        body = {}
        body['idempotency_key'] = rfc3339.rfc3339(datetime.datetime.utcnow())
        body['object'] = {}
        body['object']['type'] = 'ITEM'
        body['object']['id'] = '#' + name
        body['object']['item_data'] = {}
        body['object']['item_data']['name'] = name
        body['object']['item_data']['category_id'] = category
        body['object']['item_data']['tax_ids'] = {self.tax}
        body['object']['item_data']['variations'] = [{}]
        body['object']['item_data']['variations'][0]['type'] = "ITEM_VARIATION"
        body['object']['item_data']['variations'][0]['id'] = '#' + name + 'Variation'
        body['object']['item_data']['variations'][0]['item_variation_data'] = {}
        body['object']['item_data']['variations'][0]['item_variation_data']['price_money'] = {}
        body['object']['item_data']['variations'][0]['item_variation_data']['price_money']['amount'] = int(price * 100)
        body['object']['item_data']['variations'][0]['item_variation_data']['price_money']['currency'] = "USD"
        body['object']['item_data']['variations'][0]['item_variation_data']['pricing_type'] = 'FIXED_PRICING'
        body['object']['item_data']['variations'][0]['item_variation_data']['track_inventory'] = True
        body['object']['item_data']['variations'][0]['item_variation_data']['inventory_alert_threshold'] = 1
        body['object']['item_data']['variations'][0]['item_variation_data']['inventory_alert_type'] = 'LOW_QUANTITY'
        body['object']['item_data']['variations'][0]['item_variation_data']['sku'] = sku
        result = self.cat_api.upsert_catalog_object(body)

        if result.is_success():
            print(result.body)
            return True
        elif result.is_error():
            print(result.errors)
            return False


class SquareCategory(models.Model):
    sq_cat_id = models.CharField(max_length=30)
    sq_cat_name = models.CharField(max_length=200)

    def __str__(self):
        return self.sq_cat_name + " (" + self.sq_cat_id + ")"


class SquareInventoryItem(models.Model):
    sq_inventory = models.ForeignKey('SquareLink', on_delete=models.CASCADE)
    local_item = models.OneToOneField(InventoryItem, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    barcode = models.CharField(max_length=200)
    item_id = models.CharField(max_length=200)
    variation_id = models.CharField(max_length=200)
    category_id = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)

    @classmethod
    def from_api_dict(cls, sq_inv, api_dict):
        latest_variation = None
        latest_time = None
        item_id = None
        sku = None
        name = None
        price = None
        category_id = None
        desc = None
        data = {}

        try:
            for variation in api_dict['item_data']['variations']:
                if latest_time is None or \
                        datetime.datetime.utcfromtimestamp(latest_variation['updated_at']) \
                        < datetime.datetime.utcfromtimestamp(variation['updated_at']):
                    latest_variation = variation
            data = api_dict['item_data']
            variation_data = latest_variation['item_variation_data']
            sku = variation_data['sku']
            name = data['name']
            price = variation_data['price_money']['amount']
            item_id = variation_data['item_id']
            variation_id = latest_variation['id']

        except KeyError:
            variation_data = api_dict['item_variation_data']
            sku = variation_data['sku']
            price = variation_data['price_money']['amount']
            item_id = variation_data['item_id']
            variation_id = api_dict['id']

        try:
            desc = data['description']
            category_id = data['category_id']

        except KeyError:
            pass

        sq_inv_item, sii_created = SquareInventoryItem.objects.get_or_create(
            sq_inventory=sq_inv,
            item_id=item_id,
            barcode=sku,

            defaults={
                'variation_id': variation_id,
                'category_id': category_id,
            }

        )
        sq_inv_item.update_local_details(sq_inv)
        sq_inv_item.variation_id = variation_id
        sq_inv_item.category_id = category_id
        product = None
        if sq_inv_item.local_item is None:
            # Create or get local inventory item and product

            product = sq_inv_item.get_or_create_local_product()

            sq_inv_item.local_item, ii_created = InventoryItem.objects.get_or_create(
                partner=sq_inv.partner,  # one per partner
                product=product,
                defaults={
                    'price': Money(price / 100, "USD"),
                }
            )
            sq_inv_item.local_item.product.all_retail = True
            sq_inv_item.local_item.product.save()
            # Consider changing this so not all square items go to all retail by default

        else:
            product = sq_inv_item.local_item.product

        sq_inv_item.local_item.price = Money(price / 100, "USD")
        sq_inv_item.local_item.save()
        product.save()
        sq_inv_item.save()
        return sq_inv_item

    def get_or_create_local_product(self):
        try:
            # Get local product and associate it with this inventory item
            product = Product.objects.get(barcode=self.barcode)
        except Product.DoesNotExist:
            # or create it
            product = Product.objects.create(
                name=self.name,
                barcode=self.barcode,
                description=self.description
            )
        except Product.MultipleObjectsReturned:
            raise Exception("Two or more products exist with {} as a barcode".format(self.barcode))
        return product

    def update_local_stock(self, sq_inv=None):
        if sq_inv is None:
            sq_inv = self.sq_inventory
        sq_inv.connect()
        self.local_item.current_inventory = sq_inv.get_item_quantity(self)
        self.local_item.save()
        self.save()

    def add_square_stock(self, quantity, sq_inv=None):
        if sq_inv is None:
            sq_inv = self.sq_inventory
        sq_inv.connect()
        sq_inv.add_square_stock(self, quantity=quantity)
        self.update_local_stock(sq_inv=sq_inv)

    def update_local_details(self, sq_inv=None):
        if sq_inv is None:
            sq_inv = self.sq_inventory
        sq_inv.connect()
        result = sq_inv.cat_api.retrieve_catalog_object(self.item_id)
        if result.is_success():
            print(result)
            data = result.body['object']['item_data']
            self.name = data['name']
            self.category_id = data['category_id']
            result = sq_inv.cat_api.retrieve_catalog_object(self.category_id)
            if result.is_success():
                print(result.body)
                data = result.body['object']['category_data']
                self.category = data['name']
            else:
                print(result.errors)
        else:
            print(result.errors)
