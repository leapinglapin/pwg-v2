import datetime
import os

from django.core.management.base import BaseCommand

from partner.models import Partner
from partner.views import create_csv


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('Partner', type=str)

    def handle(self, *args, **options):
        search = options['Partner']
        if not search:
            print("Please specify partner")
            return

        partners = Partner.objects.filter(name__search=search)
        partner = None
        if partners.count() == 1:
            partner = partners.first()
            print(partner)
        else:
            print("Please choose a distributor:")
            print(partners)
            return

        filename = 'reports/{}/transaction_report_report_{}.csv'.format(partner.name, datetime.date.today().isoformat())
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='') as csvfile:
            create_csv(partner, csvfile, print_count=True)
