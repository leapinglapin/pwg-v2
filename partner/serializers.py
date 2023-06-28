from rest_framework import serializers

from .models import *


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ('name', 'slug', 'in_store_tax_rate', 'address_and_hours_info')
