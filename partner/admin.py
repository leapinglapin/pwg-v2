from django.contrib import admin

from partner.models import PartnerTransaction, PartnerAddress


class PartnerTransactionAdmin(admin.ModelAdmin):
    search_fields = ['partner__name', 'type']

admin.site.register(PartnerTransaction, PartnerTransactionAdmin)

admin.site.register(PartnerAddress)