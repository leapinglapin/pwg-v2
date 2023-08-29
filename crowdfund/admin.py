from django.contrib import admin

# Register your models here.
from crowdfund.models import CrowdfundCampaign, Reward, Backer

admin.site.register(CrowdfundCampaign)
admin.site.register(Reward)
admin.site.register(Backer)
