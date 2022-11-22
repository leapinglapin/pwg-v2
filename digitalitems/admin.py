from django.contrib import admin

# Register your models here.
from digitalitems.models import *

admin.site.register(DigitalItem)
admin.site.register(DIFile)
admin.site.register(Downloadable)