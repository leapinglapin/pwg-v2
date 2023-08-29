from django.core.management import BaseCommand
from djmoney.money import Money
from tqdm import tqdm

from billing.models import BillingEvent
from partner.models import PartnerTransaction


class Command(BaseCommand):

    def handle(self, *args, **options):
        non_ic_transactions = PartnerTransaction.objects.exclude(transaction_fees=Money('.10', "USD")).exclude(
            is_summary=True)
        old_transactions = non_ic_transactions.filter(migrated_to__isnull=True)
        pbar = tqdm(total=old_transactions.count(), unit="transactions")
        non_migrated = []
        for transaction in old_transactions:
            pbar.update(1)
            event_type = None
            user = None
            cart = None
            email = None
            timestamp = transaction.timestamp
            subtotal = None
            processing_fee = None
            platform_fee = None
            final_total = transaction.partner_cut
            if transaction.type == PartnerTransaction.PURCHASE:
                event_type = BillingEvent.COLLECTED_FROM_CUSTOMER
                if transaction.cart:
                    cart = transaction.cart
                    user = cart.owner
                    email = cart.email
                    if email is None and user is not None:
                        email = user.email
                else:
                    non_migrated.append(transaction)
                platform_fee = transaction.transaction_fees
                subtotal = final_total + platform_fee
            if transaction.type == PartnerTransaction.PAYMENT:
                if final_total.amount > 0:  # Positive means it's a payment from the partner
                    event_type = BillingEvent.PAYMENT
                else:
                    event_type = BillingEvent.PAYOUT
                processing_fee = transaction.transaction_fees
                subtotal = final_total + processing_fee
            if transaction.type == PartnerTransaction.PLATFORM_CHARGE:
                event_type = BillingEvent.DEVELOPMENT_CHARGE
                platform_fee = transaction.partner_cut
            if event_type is not None:
                billing_event = BillingEvent.objects.create(
                    partner=transaction.partner,
                    user=user,
                    email_at_time_of_event=email,
                    type=event_type,
                    timestamp=timestamp,
                    subtotal=subtotal,
                    processing_fee=processing_fee,
                    platform_fee=platform_fee,
                    final_total=final_total,
                    migrated_from=transaction,
                    cart=cart,
                )
            else:
                non_migrated.append(transaction)
        pbar.close()
        print("\n Non-migrated events: {}".format(len(non_migrated)))
        print(non_migrated)

        print("Fixing missing comments:")
        for transaction in tqdm(non_ic_transactions.filter(comments__isnull=False,
                                                           migrated_to__comments__isnull=True),
                                unit="events"):
            billing_event = transaction.migrated_to.get()  # Should only ever be 1 for non-integration charges.
            billing_event.comments = transaction.comments
            billing_event.save()
        print("Fixing missing carts:")
        for transaction in tqdm(non_ic_transactions.filter(cart__isnull=False,
                                                           migrated_to__cart__isnull=True),
                                unit="events"):
            billing_event = transaction.migrated_to.get()  # Should only ever be 1 for non-integration charges.

            billing_event.cart = transaction.cart
            billing_event.save()
        print("Fixing missing subtotals on payments:")
        for transaction in tqdm(
                non_ic_transactions.filter(transaction_subtotal__isnull=False, type=PartnerTransaction.PAYMENT,
                                           migrated_to__subtotal__isnull=True),
                unit="events"):
            billing_event = transaction.migrated_to.get()  # Should only ever be 1 for non-integration charges.
            billing_event.subtotal = transaction.partner_cut + transaction.transaction_fees
            billing_event.save()
        print("Fixing missing platform fee on development charges:")
        for transaction in tqdm(
                non_ic_transactions.filter(type=PartnerTransaction.PLATFORM_CHARGE,
                                           migrated_to__platform_fee=0),
                unit="events"):
            billing_event = transaction.migrated_to.get()  # Should only ever be 1 for non-integration charges.
            billing_event.platform_fee = transaction.partner_cut
            billing_event.save()
