from django.core.management.base import BaseCommand
from tqdm import tqdm

from shop.models import ProductImage


class Command(BaseCommand):
    def handle(self, *args, **options):
        p_images = ProductImage.objects.filter(migrated_to__isnull=True).order_by('-id')
        pbar = tqdm(total=p_images.count(), unit="image")
        for p_image in p_images:
            pbar.update(1)
            image, success = p_image.migrate()
            if success:
                status = "Success"
            else:
                status = "Error"
                print("Something went wrong, exiting!")
                exit()
