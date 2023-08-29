from django.contrib import admin

# Register your models here.
from subscriptions.models import SubscriptionCampaign, SubscriptionPack, SubscriptionData, SubscriptionTier

admin.site.register(SubscriptionCampaign)
admin.site.register(SubscriptionPack)
admin.site.register(SubscriptionData)
admin.site.register(SubscriptionTier)