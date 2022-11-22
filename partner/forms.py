from django import forms
from django.contrib.auth.models import User
from django.forms import widgets

from partner.models import PartnerTransaction
from shop.models import Publisher


class FiltersForm(forms.Form):
    search = forms.CharField(required=False)


class DiscountForm(forms.Form):
    publisher = forms.ModelChoiceField(Publisher.objects.all().order_by('name'), required=False)
    multiplier = forms.DecimalField(required=True)
    base_on_msrp = forms.BooleanField(required=False)


class BanForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_active']


class StaffLogPaymentForm(forms.ModelForm):
    class Meta:
        model = PartnerTransaction
        fields = ['type', 'transaction_subtotal', 'transaction_fees', 'comments']
        help_texts = {'transaction_subtotal': 'negative for a payout, do not include fee',
                      'transaction_fees': 'positive or zero for a payout'}

class FinancialRangeForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()
