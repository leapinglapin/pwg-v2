import b2sdk
from django.core.management.base import BaseCommand, CommandError

from digitalitems.models import DIFile


class Command(BaseCommand):
    def handle(self, *args, **options):
        files = DIFile.objects.filter(azure_file=None).order_by('id')
        for file in files:
            if not file.azure_file:
                print(file)
                print("{}/{}".format(file.id, files.count()))
                print(file.b2_file)
                print(file.azure_file)
                try:
                    file.azure_file = file.b2_file.file
                    file.save()
                except b2sdk.exception.FileNotPresent:
                    pass
