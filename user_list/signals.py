from allauth.account.adapter import get_adapter
from allauth.account.signals import email_confirmed
from allauth.account.utils import user_email, cleanup_email_addresses
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver

from user_list.models import EmailImport


@receiver(email_confirmed)
def my_callback(request, email_address, **kwargs):
    original = EmailImport.objects.filter(plaintext__iexact=email_address.email)
    if original.exists():
        original.first().try_match()


@receiver(social_account_added)
def add_email_to_account(request, sociallogin, **kwargs):
    if hasattr(sociallogin, 'email_addresses') and sociallogin.email_addresses:
        add_social_email(request, sociallogin.user, sociallogin.email_addresses)


def add_social_email(request, user, addresses):
    """
    Adds email addresses for a user that just linked a social account.
    """
    from .models import EmailAddress
    existing_addresses = EmailAddress.objects.filter(user=user)
    existing_addresses_lower = []
    for existing_address in existing_addresses:
        existing_addresses_lower.append(existing_address.email.lower().strip())
    for new_address in addresses:
        if new_address.email.lower().strip() not in existing_addresses_lower:
            new_address.primary = False
            new_address.user = user
            new_address.save()
    EmailAddress.objects.fill_cache_for_user(user, EmailAddress.objects.filter(user=user))
