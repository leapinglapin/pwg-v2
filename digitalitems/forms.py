from django import forms
from djmoney.forms import MoneyField
from treewidget.fields import TreeModelMultipleChoiceField

from digitalitems.models import *
from django.forms import widgets

from shop.models import Category
from subscriptions.models import SubscriptionPack


class AddEditDigital(forms.ModelForm):
    in_packs = forms.ModelMultipleChoiceField(SubscriptionPack.objects.none())

    class Meta:
        model = DigitalItem
        fields = ['derived_from_all', 'derived_from_any',
                  'featured',
                  'download_date', 'price', 'default_price',
                  'pay_what_you_want',
                  'tag_obj_files',
                  'tag_zip_files',
                  'enable_download_all']
        widgets = {
            'download_date': widgets.SelectDateWidget(years=range(2010, 2100)),
        }

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')

        super(AddEditDigital, self).__init__(*args, **kwargs)
        self.fields['in_packs'].required = False
        self.fields['in_packs'].queryset = SubscriptionPack.objects.filter(campaign__partner=partner) \
            .order_by('-pledges_to')
        packs = SubscriptionPack.objects.filter(contents=self.instance).exclude(contents__isnull=True)
        self.fields['in_packs'].initial = packs
        print(self.fields['in_packs'].initial)
        self.fields['tag_obj_files'].initial = partner.default_obj_tagging
        self.fields['tag_zip_files'].initial = partner.default_zip_tagging
        self.fields['enable_download_all'].initial = partner.default_download_all

    def save(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        product = kwargs.pop('product')
        saved_instance = super(AddEditDigital, self).save(commit=False, *args, **kwargs)
        saved_instance.partner = partner
        saved_instance.product = product
        saved_instance.save()
        saved_instance.subscription_packs.set(self.cleaned_data['in_packs'])
        saved_instance.save()
        return saved_instance


def invert_order_string(order_str):
    return order_str[1:] if order_str.startswith('-') else '-' + order_str


class FiltersForm(forms.Form):
    search = forms.CharField(required=False)

    SORT_RELEASE_DATE = "-product__release_date"
    SORT_UPDATE_DATE = "-root_downloadable__updated_timestamp"
    SORT_ALPHABETICAL = "product__name"

    SORT_OPTIONS = (
        (SORT_RELEASE_DATE, "Release Date, New-Old"),
        (invert_order_string(SORT_RELEASE_DATE), "Release Date, Old-New"),
        (SORT_ALPHABETICAL, "Name, A-Z"),
        (invert_order_string(SORT_ALPHABETICAL), "Name, Z-A"),
        (SORT_UPDATE_DATE, "Date Last Updated, New-Old"),
        (invert_order_string(SORT_UPDATE_DATE), "Date Last Updated, Old-New"),
    )

    order_by = forms.ChoiceField(choices=SORT_OPTIONS, required=False, initial=SORT_RELEASE_DATE)

    page_size = forms.IntegerField(
        required=False, widget=widgets.NumberInput(), initial=10)
    page_number = forms.IntegerField(
        required=False, widget=widgets.HiddenInput(), initial=1)

    categories = TreeModelMultipleChoiceField(required=False, queryset=Category.objects.all(),
                                              settings={'show_buttons': True, 'filtered': True},
                                              )

    categories.widget.attrs.update({'class': 'max-w-full'})

    partner = forms.ModelChoiceField(Partner.objects.filter(hide=False).order_by('name'),
                                     to_field_name='slug', required=False)
