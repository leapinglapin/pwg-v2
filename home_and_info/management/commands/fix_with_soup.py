from django.core.management.base import BaseCommand, CommandError

from home_and_info.models import CGTPage

from bs4 import BeautifulSoup


class Command(BaseCommand):
    def handle(self, *args, **options):
        for page in CGTPage.objects.all():
            html = page.body
            soup = BeautifulSoup(html, 'html5lib')
            cleaned_html = soup.body.decode_contents()
            page.body = cleaned_html
            page.save()
