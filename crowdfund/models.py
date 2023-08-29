from allauth.account.models import EmailAddress
from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models, transaction
# Create your models here.
from moneyed import Money

from partner.models import PartnerTransaction


class CrowdfundCampaign(models.Model):
    partner = models.ForeignKey("partner.Partner", on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    currency_conversion_rate = models.DecimalField(default=1, max_digits=10, decimal_places=2)
    platform_cut = models.DecimalField(default=.05, max_digits=10, decimal_places=2)
    charge_date = models.DateField()

    def __str__(self):
        return "{} from {}".format(self.name, self.partner.name)


class Reward(models.Model):
    campaign = models.ForeignKey(CrowdfundCampaign, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    external_name = models.CharField(max_length=200)

    def __str__(self):
        return "{} {}".format(self.campaign.name, self.name)

    def get_user_accounts(self):
        return AUTH_USER_MODEL.filter(id__in=self.entitled_backers.values_list("user_id", flat=True))


class BackerManager(models.Manager):
    def get_backers_for_user(self, user):
        '''
        Same as backer.records.filter(user=user), but tries to match that user to existing emails first.
        :param user:
        :return:
        '''
        # First try linking the user up to the account
        has_record_campaigns = CrowdfundCampaign.objects.filter(backer__user=user)
        potentially_this_backers_record = self.exclude(campaign__in=has_record_campaigns)
        for email in EmailAddress.objects.filter(user=user, verified=True):
            backer_options = potentially_this_backers_record.filter(email_address__iexact=email.email, user=None)
            campaigns = backer_options.values_list('campaign', flat=True).distinct()
            for campaign in campaigns:
                backer_options.filter(campaign=campaign).first().try_match()
        return self.filter(user=user)


class Backer(models.Model):
    campaign = models.ForeignKey(CrowdfundCampaign, on_delete=models.CASCADE)
    email_address = models.EmailField()
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='backer_records')
    backing_minimum = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10)
    pledge_amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10)
    rewards = models.ManyToManyField(Reward, blank=True, related_name="entitled_backers")
    tier = models.ForeignKey("CrowdfundTier", on_delete=models.CASCADE, null=True, blank=True)

    linked_charge = models.ForeignKey(PartnerTransaction, on_delete=models.SET_NULL, null=True, blank=True)

    records = BackerManager()

    def __str__(self):
        identifier = self.email_address
        if self.user:
            identifier = self.user.username
        return "{}'s {} pledge for {} ".format(identifier, self.pledge_amount, self.campaign)

    def try_match(self):
        """

        :return: the user if able to link, none if not able to link.
        """
        try:
            self.user = EmailAddress.objects.get(email__iexact=self.email_address, verified=True).user
            self.save()
            return self.user
        except EmailAddress.DoesNotExist:
            return None

    def charge_creator(self):
        """
        If there is no linked charge associated with this pledge, charge the partner associated
        the amount donated for rewards converted to USD and the agreed upon fee.
        """

        amount_to_charge = self.backing_minimum * self.campaign.currency_conversion_rate * self.campaign.platform_cut
        with transaction.atomic():
            # Select for update to ensure we don't create a new partner transaction.
            pt = PartnerTransaction.objects.select_for_update().get(id=self.id)
            if pt.linked_charge is None:
                self.linked_charge = PartnerTransaction.objects.create(partner=self.campaign.partner,
                                                                       type=PartnerTransaction.PLATFORM_CHARGE,
                                                                       transaction_total=Money(0, 'USD'),
                                                                       transaction_subtotal=Money(0, 'USD'),
                                                                       transaction_fees=Money(amount_to_charge, 'USD'))
                self.linked_charge.timestamp = self.campaign.charge_date  # Override timestamp, can't be done at create
                self.linked_charge.save()
                self.linked_charge.apply()
                self.save()


class CrowdfundTier(models.Model):
    campaign = models.ForeignKey(CrowdfundCampaign, on_delete=models.CASCADE)
    name = models.TextField(max_length=200)

    def __str__(self):
        return "{} {}".format(self.campaign, self.name)
