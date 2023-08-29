from django.core.management.base import BaseCommand, CommandError

from intake.distributors import alliance
from intake.models import *
import requests

from squarelink.models import SquareLink


class Command(BaseCommand):
    help = 'Import items from square'

    def handle(self, *args, **options):
        for squarelink in SquareLink.objects.all():
            squarelink.import_all()









