import psycopg as psycopg
from django.core.management.base import BaseCommand
from django.db import connection

update_ctype = 1

tables_to_copy = {  # Copy these tables, in order, from the old database
    "auth_user": None, # Re-enable this on first copy
    "account_emailaddress": None,
    "account_emailconfirmation": None,

    # "auth_group": None,
    # "auth_permission": None,
    # "auth_group_permissions": None,
    # "auth_user_groups": None,
    # "auth_user_user_permissions": None,

    # "django_content_type": None,
    # "django_admin_log": None,
    # "django_migrations": None, # Do not migrate the migrations table
    "django_session": None,
    "django_site": None,

    "address_country": None,
    "address_state": None,
    "address_locality": None,
    "address_address": None,
    "realaddress_realcountry": None,
    "realaddress_useraddress": None,
    "checkout_billingaddress": None,

    "partner_partner": None,
    "partner_partner_administrators": None,
    "partner_partneraddress": None,
    "partner_partnertransaction": None,

    # Games and publishers before products
    "shop_cardcondition": None,
    "shop_category": None,
    "shop_publisher": None,
    "game_info_game": None,
    "game_info_faction": None,
    "game_info_edition": None,
    "game_info_format": None,
    "game_info_attributetype": None,
    "game_info_attribute": None,
    "game_info_attribute_factions": None,
    "game_info_containspieces": None,
    "game_info_containspieces_any_of": None,

    "game_info_gamepiece": None,
    "game_info_gamepiece_attributes": None,
    "game_info_gamepiece_factions": None,
    "game_info_gamepiecevariant": None,
    "game_info_gamepiecevariant_attributes": None,

    "images_image": None,
    "shop_productimage": None,

    "shop_product": update_ctype,
    "shop_product_attached_images": None,
    "shop_product_attributes": None,
    "shop_product_categories": None,
    "shop_product_contents": None,
    "shop_product_editions": None,
    "shop_product_factions": None,
    "shop_product_formats": None,
    "shop_product_games": None,
    "shop_product_image_gallery": None,
    "shop_containsproducts": None,

    "shop_item": update_ctype,

    "shop_item_image_gallery": None,
    "shop_inventoryitem": None,
    "shop_customchargeitem": None,
    "shop_madetoorder": None,
    "shop_useditem": None,

    "shop_backorderrecord": None,

    "discount_codes_referrer": None,
    "discount_codes_discountcode": None,
    "discount_codes_discountcode_publishers": None,
    "discount_codes_partnerdiscount": None,

    "checkout_shippingaddress": None,
    "checkout_cart": None,
    "checkout_checkoutline": None,
    "shop_inventorylog": None,
    "checkout_stripecustomerid": None,
    "checkout_stripepaymentintent": None,
    "checkout_taxratecache": None,
    "checkout_userdefaultaddress": None,
    "credit_usercredit": None,
    "credit_usercreditchange": None,

    "discount_codes_codeusage": None,

    "events_event": None,
    "events_eventticketitem": None,

    "giveaway_giveaway": None,
    "giveaway_entry": None,

    "intake_categorymap": None,
    "intake_categorymap_category": None,
    "intake_distributor": None,
    "intake_distitem": None,
    "intake_traderange": None,
    "intake_distitem_trade_range": None,
    "intake_distributorwarehouse": None,
    "intake_distributorinventoryfile": None,
    "intake_itemwarehouseavailability": None,
    "intake_itemwarehouseavailability_based_on_file": None,
    "intake_manufacturer": None,
    "intake_manufacturerabbreviation": None,
    "intake_manufacturerbarcode": None,
    "intake_purchaseorder": None,
    "intake_poline": None,
    "intake_pricingrule": None,
    "inventory_report_inventoryreportlocation": None,
    "inventory_report_inventoryreport": None,
    "inventory_report_inventoryreportline": None,

    "posts_banner": None,
    "posts_post": None,
    "posts_post_attributes": None,
    "posts_post_editions": None,
    "posts_post_factions": None,
    "posts_post_formats": None,
    "posts_post_games": None,
    "posts_post_products": None,

    "socialaccount_socialaccount": None,
    "socialaccount_socialapp": None,
    "socialaccount_socialapp_sites": None,
    "socialaccount_socialtoken": None,
    "taggit_tag": None,
    "taggit_taggeditem": None,

    "user_list_userlist": None,
    "user_list_userlistentry": None,
    "user_list_emailimport": None,
    "user_list_emailinvitation": None,
    "payments_payment": update_ctype,
    "payments_cashpayment": None,
    "payments_paypalpayment": None,
    "payments_stripepayment": None,
}

tables_that_need_ctype_updated = [
    "payments_payment",
    "shop_item",
    "shop_product",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        with psycopg.connect("dbname='website_dump' user='cgt' host='localhost' password='cgt'").cursor() as src_curr:
            with connection.cursor() as dest_curr:
                command = "BEGIN; \n"  # WILL CLEAR DATA FROM TARGET
                for table in tables_to_copy:
                    command += "DELETE FROM {}; \n".format(table)
                command += "COMMIT;"
                dest_curr.execute(command)
                ctype_old_table = {}
                ctype_new_table = {}

                created_ctypes = []

                dest_curr.execute("""SELECT * from django_content_type; """)
                for ctype in dest_curr:
                    table_name = "{}_{}".format(ctype[1], ctype[2])
                    ctype_new_table[table_name] = ctype[0]

                src_curr.execute("""SELECT * from django_content_type; """)
                for ctype in src_curr:
                    table_name = "{}_{}".format(ctype[1], ctype[2])
                    ctype_old_table[table_name] = ctype[0]
                    # If the ctype is not in the new table, we need to make it in the destination,
                    # so we can still do a copy operation
                    if table_name not in ctype_new_table:
                        dest_curr.execute("""
                        INSERT INTO  django_content_type("app_label", "model")
                        VALUES ('{}', '{}')
                        RETURNING id
                        """.format(ctype[1], ctype[2]))
                        id_of_new_row = dest_curr.fetchone()[0]
                        ctype_new_table[table_name] = id_of_new_row
                        print("Creating ctype {} for {}".format(id_of_new_row, table_name))
                        created_ctypes.append(id_of_new_row)

                # Need to update item, product, and payment.
                src_curr.execute("""CREATE TEMP TABLE CTYPE_TRANSLATION(
                                                                    old_ctype_id INTEGER,
                                                                    new_ctype_id INTEGER
                                                                );
                                                                """
                                 )
                for table_name in ctype_new_table:
                    if table_name in ctype_old_table:
                        src_curr.execute("""
                                                                        INSERT INTO  CTYPE_TRANSLATION (old_ctype_id, new_ctype_id) VALUES ('{}', '{}');
                                                                        """.format(ctype_old_table[table_name],
                                                                                   ctype_new_table[table_name]))
                        print("CType {} for {} now points to {} ".format(ctype_old_table[table_name], table_name,
                                                                         ctype_new_table[table_name]))
                for table in tables_to_copy:
                    print("Copying table {}".format(table))
                    dest_curr.execute("""
SELECT column_name
  FROM information_schema.columns
   WHERE table_name   = '{}'
                                                """.format(table))
                    columns = [row[0] for row in dest_curr]  # tuple to list
                    columns = ['"{}"'.format(column) for column in columns]  # add quotes around names
                    columns_list = ', '.join(columns)  # make a string for input
                    columns_list_old = columns_list
                    columns_list_new = columns_list

                    copy_command = "COPY public.{} ({}) TO STDOUT".format(table, columns_list_old)

                    if "polymorphic_ctype_id" in columns_list_old:
                        # we need to join the translation table with the table we're copying
                        # and use the new ctype instead of the old one.
                        columns_list_old = columns_list_old.replace("polymorphic_ctype_id", "new_ctype_id")
                        copy_command = """
                        COPY  (select {} from public.{} INNER JOIN CTYPE_TRANSLATION ON old_ctype_id = polymorphic_ctype_id) TO STDOUT;
                        """.format(columns_list_old, table)
                        src_curr.execute(
                            "select {} from public.{} INNER JOIN CTYPE_TRANSLATION ON old_ctype_id = polymorphic_ctype_id".format(
                                columns_list_old, table))

                    try:
                        with src_curr.copy(copy_command) as src_copy:
                            with dest_curr.copy(
                                    "COPY public.{} ({}) FROM STDIN".format(table, columns_list_new)) as dest_copy:
                                for data in src_copy:
                                    dest_copy.write(data)
                    except psycopg.errors.UniqueViolation:  # We expect this error if the data for this table was already copied
                        print("\tData from {} has already been copied".format(table))
                    if "polymorphic_ctype_id" in columns_list_new:
                        for ctype in created_ctypes:
                            dest_curr.execute("DELETE FROM {} where polymorphic_ctype_id={}".format(table, ctype))
