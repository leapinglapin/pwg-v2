from django.contrib import admin
from .models import *


class PledgeDataAdmin(admin.ModelAdmin):
    search_fields = ['email']


admin.site.register(PatreonCampaign)
admin.site.register(PledgeData, PledgeDataAdmin)
