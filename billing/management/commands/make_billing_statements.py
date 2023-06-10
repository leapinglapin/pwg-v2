import datetime

from django.core.management import BaseCommand
from tqdm import tqdm

from billing.models import BillingEvent, BillingStatement, PartnerBalance
from partner.models import Partner


class Command(BaseCommand):

    def handle(self, *args, **options):
        event_count = BillingEvent.objects.filter(statement__isnull=True).count()
        pbar = tqdm(total=event_count, unit="events")

        for partner in Partner.objects.all():
            PartnerBalance.objects.get_or_create(partner=partner)
            events = BillingEvent.objects.filter(partner=partner, statement__isnull=True)
            if events.exists():
                start_year = events.first().timestamp.year
                for year in range(start_year, datetime.date.today().year + 1):
                    for month in range(1, 13):
                        # Get monthly statement.
                        statement, _ = BillingStatement.objects.get_or_create(partner=partner,
                                                                              statement_start=datetime.date(year=year,
                                                                                                            month=month,
                                                                                                            day=1))
                        statement.finalized = False  # De-finalize statements for this initial dataload
                        for event in events.filter(timestamp__year=year, timestamp__month=month):
                            pbar.update(1)
                            if event.add_to_statement(statement):
                                # successfully added
                                pass
                            else:
                                # Add line to next statement?
                                pass
        print("Balance per partner")
        for partner in Partner.objects.all():
            print("{}: {}".format(partner, partner.partnerbalance.get_calculated_balance()))
            for statement in BillingStatement.objects.filter(partner=partner).order_by("statement_start"):
                total = statement.get_statement_total()
                if total:
                    print("\t{}/{}: {}".format(statement.statement_start.year, statement.statement_start.month,
                                               total))
                    statement.finalize()
