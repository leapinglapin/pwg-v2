import datetime

from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models, transaction
from django.db.models import Sum
# Create your models here.
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from partner.models import PartnerTransaction


class PartnerBalance(models.Model):
    partner = models.OneToOneField('partner.Partner', on_delete=models.CASCADE, null=True, blank=True)
    balance = MoneyField(max_digits=8, decimal_places=2, default_currency='USD', default=Money('0', 'USD'))

    def get_calculated_balance(self):
        events = BillingEvent.objects.filter(partner=self.partner)
        return events.aggregate(Sum('final_total'))['final_total__sum']


class BillingStatement(models.Model):
    partner = models.ForeignKey("partner.Partner", on_delete=models.CASCADE)
    statement_start = models.DateField()
    finalized = models.BooleanField(default=False)

    class Meta:
        ordering = ['statement_start', ]

    def __str__(self):
        return "Statement {}: {}/{}".format(self.id, self.statement_start.year, self.statement_start.month)

    def get_statement_total(self):
        amount = self.events.aggregate(Sum('final_total'))['final_total__sum']
        if amount:
            return Money(amount, "USD")
        return Money(0, 'USD')

    def get_balance_at_end_of_statement(self):
        '''
        This sums all events from before and during this statement.
        :return: The partners balance at the time of that statement
        '''
        amount = BillingEvent.objects.filter(partner=self.partner,
                                                   statement__isnull=False,
                                                   statement__statement_start__lte=self.statement_start).aggregate(
            Sum('final_total'))['final_total__sum']
        if amount is None:
            amount = 0
        return Money(amount, "USD")

    def get_balance_before_statement(self):
        '''
        This sums all events from before and during this statement.
        :return: The partners balance at the time of that statement
        '''
        amount = BillingEvent.objects.filter(partner=self.partner,
                                             statement__isnull=False,
                                             statement__statement_start__lt=self.statement_start).aggregate(
            Sum('final_total'))['final_total__sum']
        if amount is None:
            amount = 0
        return Money(amount, "USD")

    def get_summary(self):
        summary = {}
        for event_type in BillingEvent.BILLING_EVENT_TYPES:
            amount = self.events.filter(type=event_type[0]).aggregate(Sum('final_total'))['final_total__sum']
            if amount:
                summary[event_type[1]] = Money(amount, "USD")
        return summary

    def integration_charges_by_pack(self):
        summary = {}

        # distinct requires order_by

        return summary

    def is_past_month(self):
        return self.statement_start.year < datetime.date.today().year \
            or (self.statement_start.year == datetime.date.today().year
                and self.statement_start.month < datetime.date.today().month)

    def finalize(self):
        if self.is_past_month():
            self.finalized = True
            self.save()


class BillingEvent(models.Model):
    statement = models.ForeignKey('BillingStatement', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="events")

    INTEGRATION_CHARGE, COLLECTED_FROM_CUSTOMER, REFUND_TO_CUSTOMER, DEVELOPMENT_CHARGE, PAYOUT, PAYMENT, OTHER = (
        "IC", "CC", "CR", "DC", "PO", "PI", "O?")
    BILLING_EVENT_TYPES = (
        (INTEGRATION_CHARGE, "Integration Charge"),
        (COLLECTED_FROM_CUSTOMER, "Collected from Customer"),
        (DEVELOPMENT_CHARGE, "Charge for Custom Development"),
        (PAYOUT, "A payment to the partner"),
        (PAYMENT, "A payment collected from the partner"),
        (OTHER, "Other")
    )
    type = models.CharField(
        "type", max_length=3, default=None, choices=BILLING_EVENT_TYPES, null=True)

    partner = models.ForeignKey("partner.Partner", on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    email_at_time_of_event = models.EmailField(blank=True, null=True)

    timestamp = models.DateTimeField()

    subtotal = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', blank=True, null=True)
    processing_fee = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', blank=True, null=True,
                                help_text="Fees from 3rd party services, generally for payouts")
    platform_fee = MoneyField(max_digits=14, decimal_places=2, default_currency='USD',
                              help_text="Fees from the platform", null=True, blank=True)
    final_total = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    applied_to_account = models.BooleanField(default=False)
    balance_after_apply = MoneyField(max_digits=14, decimal_places=4, default_currency='USD', blank=True, null=True)

    comments = models.TextField(blank=True, null=True)

    migrated_from = models.ForeignKey(PartnerTransaction, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="migrated_to")

    cart = models.ForeignKey("checkout.Cart", on_delete=models.PROTECT, null=True, blank=True,
                             related_name="billing_event")

    pledge_month = models.DateField(blank=True, null=True)  # first day of the month in question

    class Meta:
        ordering = ['timestamp', ]

    def apply(self):
        with transaction.atomic():
            b_event = BillingEvent.objects.select_for_update().get(id=self.id)  # Use lock on object
            if not b_event.applied_to_account:
                partner_balance, _ = PartnerBalance.objects.select_for_update().get_or_create(partner=self.partner)
                balance = partner_balance.save
                balance = balance + b_event.final_total
                b_event.balance_after_apply = balance
                partner_balance.balance = balance
                partner_balance.save()
                b_event.applied_to_account = True
                b_event.save()

    def add_to_statement(self, statement):
        if not statement.finalized:
            self.statement = statement
            self.save()
            return True
        return False

    def type_longform(self):
        type_dict = dict(self.BILLING_EVENT_TYPES)
        return type_dict[self.type]

    def __str__(self):
        return "{} {} {} {} {}".format(self.id, self.partner.name, self.type, self.subtotal, self.timestamp)
