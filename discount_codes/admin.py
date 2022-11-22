from django.contrib import admin

from .models import DiscountCode, Referrer, PartnerDiscount, CodeUsage

# Register your models here.
admin.site.register(DiscountCode)
admin.site.register(Referrer)
admin.site.register(PartnerDiscount)
admin.site.register(CodeUsage)
