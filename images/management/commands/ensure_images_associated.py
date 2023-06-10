from django.core.management.base import BaseCommand
from tqdm import tqdm

from shop.models import ProductImage, Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        products_with_new_images = Product.objects.filter(primary_image__isnull=False).count()
        products_with_old_images = Product.objects.filter(main_image__isnull=False).count()
        print("{} of {} images have been properly associated ({}%)".format(products_with_new_images,
                                                                           products_with_old_images,
                                                                           products_with_new_images / products_with_old_images))
        p_images = ProductImage.objects.order_by('-id')

        pbar = tqdm(total=p_images.count(), unit="image", desc="Images checked")
        associated_bar = tqdm(total=products_with_old_images, unit="product", desc="Products associated with images")

        for p_image in p_images:
            pbar.update(1)
            if p_image.migrated_to is None:
                p_image.migrate()
            if p_image.migrated_to and p_image.migrated_to.id:
                new_image = p_image.migrated_to
                for product in p_image.product_set.all():
                    product.primary_image = new_image
                    product.attached_images.add(new_image)
                    product.save()
                    associated_bar.update(1)
                for product in p_image.partner_images.all():
                    product.attached_images.add(new_image)
                    product.save()
