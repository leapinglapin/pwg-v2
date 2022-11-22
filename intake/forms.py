import decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from djmoney.forms import MoneyField
from djmoney.money import Money

from shop.forms import AddProductForm
from .models import PricingRule, PurchaseOrder, POLine, DistributorInventoryFile


class RefreshForm(forms.Form):
    distributor = forms.CharField(required=False)
    purchase_order = forms.CharField(required=False)
    add_mode = forms.BooleanField(required=False)
    auto_load = forms.BooleanField(required=False)
    auto_print_mode = forms.BooleanField(required=False)
    barcode = forms.CharField(required=False)
    quantity = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        super(RefreshForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get("quantity")
        if quantity < 0:
            msg = ValidationError("Quantity must not be negative")
            self.add_error('quantity', msg)


class AddForm(AddProductForm):
    our_price = MoneyField(default_currency='USD')


class UploadInventoryForm(forms.ModelForm):
    class Meta:
        model = DistributorInventoryFile
        fields = ['distributor', 'file']


class PrintForm(forms.Form):
    print_msrp = forms.CharField(required=False, widget=HiddenInput)
    print_price = forms.CharField(required=True, widget=HiddenInput)
    print_name = forms.CharField(required=False, widget=HiddenInput)


class PricingRuleForm(forms.ModelForm):
    class Meta:
        model = PricingRule
        fields = ['percent_of_msrp', 'priority', 'publisher', 'use_MAP']


class POForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['distributor', 'date', 'po_number', 'subtotal', 'amount_charged']


class POLineForm(forms.ModelForm):
    subtotal = MoneyField(default_currency='USD', required=False)

    class Meta:
        model = POLine
        fields = ['name', 'barcode', 'cost_per_item', 'expected_quantity', 'received_quantity', 'subtotal',
                  'line_number']

    def __init__(self, *args, **kwargs):
        # partner = kwargs.pop('partner')
        # distributor = kwargs.pop('distributor')
        super(POLineForm, self).__init__(*args, **kwargs)
        self.fields['cost_per_item'].required = False
        self.fields['cost_per_item'].help_text = "Set cost per line or subtotal and quantity"

        # products = Product.objects.filter(all_retail=True) | Product.objects.filter(partner=partner)
        # self.fields['product'].queryset = products.distinct().order_by('name')
        # self.fields['item'].queryset = DistItem.objects.filter(distributor=distributor).order_by('dist_name')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['subtotal'] and not cleaned_data['cost_per_item']:
            cpi = cleaned_data['subtotal'] / cleaned_data['expected_quantity']
            TWO_PLACES = decimal.Decimal("0.0001")
            cpi = Money(cpi.amount.quantize(TWO_PLACES), 'USD', decimal_places=4)
            cleaned_data['cost_per_item'] = cpi
        return cleaned_data
