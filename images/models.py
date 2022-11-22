from django.db import models
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFit

from images.PublicAzureStorage import PublicAzureStorage
from partner.models import Partner


class Image(models.Model):
    image_src = models.ImageField(upload_to='images', storage=PublicAzureStorage)
    banner_full = ImageSpecField(source='image_src',
                                 processors=[ResizeToFit(1800, 480)],
                                 options={'quality': 60})
    product_gallery_thumb = ImageSpecField(source='image_src',
                                           processors=[ResizeToFit(100, 100)],
                                           options={'quality': 60})

    alt_text = models.CharField(max_length=200, blank=True, null=True,
                                help_text="Used in screen readers for the visually impared. " +
                                          " Blank to default to filename")
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return "{} image ({}) from {}".format(self.alt_text, self.id, self.partner)

    def save(self, *args, **kwargs):
        if not self.alt_text:
            # Set alt text to the filename, without the extension, and replace underscores with spaces
            self.alt_text = ".".join(self.image_src.name.split('.')[:-1]).replace('_', ' ')
        return super(Image, self).save(*args, **kwargs)
