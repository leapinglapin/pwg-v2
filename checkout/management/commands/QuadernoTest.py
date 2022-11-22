import os
import sys
import urllib.parse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import traceback
import requests

from checkout.models import Cart


class Command(BaseCommand):
    def handle(self, *args, **options):
        params = {'to_country': "GB"}
        params = urllib.parse.urlencode(params)
        suffix = "tax_rates/calculate?{}".format(params)
        print("{}{}".format(settings.QUADERNO_URL, suffix))
        response = requests.get(
            "{}{}".format(settings.QUADERNO_URL, suffix),
            auth=(settings.QUADERNO_PRIVATE, "x"),
            headers={
                'User-Agent': "CG&T",
            }
        )
        print(response)
        print(response.json())
