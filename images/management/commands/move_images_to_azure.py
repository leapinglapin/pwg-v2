import b2sdk
from b2sdk.exception import FileNotPresent
from django.core.management.base import BaseCommand, CommandError

from images.models import Image
from shop.models import Product, ProductImage


class Command(BaseCommand):
    def handle(self, *args, **options):
        p_images = ProductImage.objects.all().order_by('-id')
        i = 1
        for p_image in p_images:
            image, success = p_image.migrate()
            print(image, success)
            if success:
                status = "Success"
            else:
                status = "Error"
            print("{}/{}: {}: {}".format(i, p_images.count(), status, p_image))
            i += 1
            exit()
