from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Partner


class PartnerAdmin(ModelAdmin):
    model = Partner


modeladmin_register(PartnerAdmin)
