from django import forms

from .models import *


class PatreonAPIForm(forms.ModelForm):
    class Meta:
        model = PatreonCampaign
        fields = ['creator_access_token', 'creator_refresh_token']
