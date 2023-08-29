import urllib.parse

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        params = {'to_country': "GB"}
        params = urllib.parse.urlencode(params)
        tests = [params]
        tests.append("to_country=US&to_city=Verona&to_postal_code=53593")
        url = settings.QUADERNO_URL
        private_key = settings.QUADERNO_PRIVATE
        for params in tests:
            suffix = "tax_rates/calculate?{}".format(params)
            print("{}{}".format(url, suffix))
            response = requests.get(
                "{}{}".format(url, suffix),
                auth=(private_key, "x"),
                headers={
                    'User-Agent': "PWG",
                }
            )
            print(response)
            print(response.json())
            print(response.json()['rate'])
            print("\n")
