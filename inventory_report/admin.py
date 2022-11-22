from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(InventoryReport)
admin.site.register(InventoryReportLocation)
admin.site.register(InventoryReportLine)
