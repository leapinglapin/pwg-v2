import stripe
from address.forms import AddressField
from address.widgets import AddressWidget
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError

from checkout.models import Cart, UserDefaultAddress
from .models import *
from django.forms import widgets, HiddenInput, RadioSelect


class TierForm(forms.ModelForm):
    class Meta:
        model = SubscriptionTier
        fields = ['tier_name', 'external_name', 'price', 'default_price', 'limit', 'allow_on_site_subscriptions']

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        campaign = kwargs.pop('campaign')
        super(TierForm, self).__init__(*args, **kwargs)

    def save_to_patreon(self, campaign):
        new_discount = self.save(commit=False)
        new_discount.campaign = campaign
        self.save()


class PackForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPack
        fields = ['name', 'contents', 'pledges_from', 'pledges_to', 'tier_req', 'require_multiple_months',
                  'number_of_months', 'require_exact_months', 'token', 'token_quantity']
        widgets = {
            'pledges_to': AdminDateWidget(),
            'pledges_from': AdminDateWidget(),
            'tier_req': widgets.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        campaign = kwargs.pop('campaign')
        super(PackForm, self).__init__(*args, **kwargs)
        self.fields['contents'].queryset = DigitalItem.objects.filter(partner=partner).order_by(
            'product__name').order_by('product__release_date')
        self.fields['pledges_to'].help_text = "For the end date, select the first of the month after the pledge period ends. EX: For January 2021 pledges, make the end date Feb. 1st 2021."
        self.fields['tier_req'].queryset = SubscriptionTier.objects.filter(campaign=campaign)
        self.fields['require_exact_months'].help_text = \
            "Require exact months sets the start date to the necessary" + \
            " date for the loyalty reward to only cover those months"

    def clean(self):
        cleaned_data = super().clean()
        pledges_to = cleaned_data.get("pledges_to")
        pledges_from = cleaned_data.get("pledges_from")
        if pledges_to and pledges_from:
            if pledges_to < pledges_from:
                self.add_error("pledges_to", "Start date must be before end date")
        if pledges_to.month == pledges_from.month and pledges_to.year == pledges_from.year:
            self.add_error("pledges_from", "Start and end dates must be different months")
        require_multiple_months = cleaned_data.get('require_multiple_months')
        number_of_months = cleaned_data.get('number_of_months')
        if require_multiple_months:
            if number_of_months <= 1:
                self.add_error("number_of_months", "Number of months must be greater than 1")
            if number_of_months is None:
                self.add_error("number_of_months", "Number of months required")

    def save_to_patreon(self, campaign):
        new_pack = self.save(commit=False)
        new_pack.campaign = campaign
        self.save()


class DiscountForm(forms.ModelForm):
    class Meta:
        model = SubscriberDiscount
        fields = ['tier_req', 'price_multiplier', 'start_month', 'day_of_month_start', 'day_of_month_end', 'repeat',
                  'paused', 'last_month_before_pause']
        widgets = {
            'start_month': AdminDateWidget(),
            'last_month_before_pause': AdminDateWidget(),
            'tier_req': widgets.CheckboxSelectMultiple()
        }

    def clean(self):
        cleaned_data = super().clean()
        pledges_to = cleaned_data.get("pledges_to")
        paused = cleaned_data.get('paused')
        month = cleaned_data.get('last_month_before_pause')
        if paused:
            if month is None:
                self.add_error("last_month_before_pause", "Paused month required when paused")

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        campaign = kwargs.pop('campaign')
        super(DiscountForm, self).__init__(*args, **kwargs)
        self.fields['tier_req'].queryset = SubscriptionTier.objects.filter(campaign=campaign)

    def save_to_patreon(self, campaign):
        new_discount = self.save(commit=False)
        new_discount.campaign = campaign
        self.save()


class GrantManualAccessForm(forms.Form):
    pack = forms.ModelChoiceField(SubscriptionPack.objects.all())
    tier = forms.ModelChoiceField(SubscriptionTier.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        super(GrantManualAccessForm, self).__init__(*args, **kwargs)
        self.fields['pack'].queryset = SubscriptionPack.objects.filter(campaign__partner=partner)
        self.fields['tier'].queryset = SubscriptionTier.objects.filter(campaign__partner=partner)

    def save(self, user):
        if self.is_valid():  # validate the form
            pack = self.cleaned_data['pack']
            tier = self.cleaned_data['tier']
            print("User: ", user)

            # Create pledge
            pack.add_to_downloads_for_user(user, date=pledge.date)
        else:
            print("Form is not valid")
            print(self)


class RevokeManualAccessForm(forms.Form):
    pack = forms.ModelChoiceField(SubscriptionPack.objects.all())

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        super(RevokeManualAccessForm, self).__init__(*args, **kwargs)
        self.fields['pack'].queryset = SubscriptionPack.objects.filter(campaign__partner=partner)

    def save(self, user):
        if self.is_valid():  # validate the form
            pack = self.cleaned_data['pack']
            print("User: ", user)
            # Delete data associated with this pack
            for item in pack.contents.all():
                for purchase in item.downloads.filter(user=user):
                    purchase.delete()

            # Ensure orders from purchases still exist
            for cart in Cart.submitted.filter(owner=user):
                cart.create_purchases()  # create_purchases will check that the items aren't already purchased
        else:
            print("Form is not valid")
            print(self)


class UserDefaultAddressForm(forms.ModelForm):
    class Meta:
        model = UserDefaultAddress
        fields = ['address']
        widgets = {'address': AddressWidget()}


class OnboardingForm(forms.ModelForm):
    start_now = forms.BooleanField(initial=True, help_text="If you already have a subscription through an alternate "
                                                           "service, uncheck this box. "
                                                           "Remember to cancel on that platform!")
    address = AddressField()

    class Meta:
        model = SubscriberList
        fields = ['tier', 'payment_method']
        widgets = {'payment_method': HiddenInput(), 'tier': RadioSelect()}

    def __init__(self, *args, **kwargs):
        campaign = kwargs.pop('campaign')
        user = kwargs.pop('user')
        super(OnboardingForm, self).__init__(*args, **kwargs)
        print(campaign)
        self.fields['tier'].queryset = campaign.tiers.filter(allow_on_site_subscriptions=True)

        if user:
            if hasattr(user, "default_address"):
                self.fields['address'].initial = user.default_address.address
