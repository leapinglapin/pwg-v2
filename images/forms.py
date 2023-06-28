from django import forms

from images.models import Image


class UploadImage(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image_src', 'alt_text']
