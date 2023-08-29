from django.test import TestCase

from partner.models import Partner
from subscriptions.models import SubscriptionCampaign

class PartnerTestCase(TestCase):
    def setUp(self):
        testPartner = Partner.objects.create(name="Test Partner")
        SubscriptionCampaign.objects.create(partner=testPartner)

    def test_something(self):
        """Definitely tests something"""
        self.assertEqual(1, 1)
