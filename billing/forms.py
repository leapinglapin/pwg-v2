from django import forms
from djmoney.forms import MoneyField

from billing.models import BillingEvent


class StaffLogBillingEventForm(forms.Form):
    amount = MoneyField(default_currency='USD')
    payment_processor_fees = MoneyField(default_currency='USD', required=False,
                                        help_text='Any Paypal fees,etc. positive number')
    comments = forms.CharField(widget=forms.Textarea, required=False)


class StaffLogOtherBillingEventForm(StaffLogBillingEventForm):
    type = forms.ChoiceField(choices=BillingEvent.BILLING_EVENT_TYPES)
    amount = MoneyField(default_currency='USD', help_text='Negative for a charge')
    field_order = ['type', 'amount', 'payment_processor_fees', 'comments']
