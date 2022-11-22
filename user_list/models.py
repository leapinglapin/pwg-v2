from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.db import models, transaction


class UserListManager(models.Manager):
    def lists_for_user(self, user):
        return self.filter(list_entries=user.list_entries)


class UserList(models.Model):
    lists = UserListManager
    partner = models.ForeignKey("partner.Partner", null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    editable = models.BooleanField(default=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.id)

    def import_entry(self, email):
        email = email.strip()
        email_import, _ = EmailImport.objects.get_or_create(plaintext=email)
        match = email_import.try_match()
        if match:
            self.list_entries.get_or_create(user=match.user, defaults={"opt_into_emails": True})
        else:
            # Send another invitation for the new mailing list
            invitation, created = self.emailinvitation_set.get_or_create(original=email_import)
            invitation.send()


class UserListEntry(models.Model):
    user_list = models.ForeignKey(UserList, on_delete=models.CASCADE, related_name='list_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='list_entries')
    opt_into_emails = models.BooleanField(default=False)
    expires_on = models.DateTimeField(blank=True, null=True)  # in case membership expires


class EmailImport(models.Model):
    plaintext = models.CharField(max_length=300, unique=True)
    email_address = models.ForeignKey(EmailAddress, on_delete=models.SET_NULL, null=True)

    def try_match(self):
        try:
            self.email_address = EmailAddress.objects.get(email__iexact=self.plaintext, verified=True)
            self.save()
            for invitation in self.invitations.all():
                invitation.delete()
            return self.email_address
        except EmailAddress.DoesNotExist:
            return None


class EmailInvitation(models.Model):
    original = models.ForeignKey(EmailImport, on_delete=models.CASCADE, related_name='invitations')
    user_list = models.ForeignKey(UserList, on_delete=models.CASCADE)
    invitation_sent = models.BooleanField(EmailImport, default=False)

    def send(self):
        with transaction.atomic():
            invitation = EmailInvitation.objects.select_for_update().get(id=self.id)
            # Send the email here
            invitation.invitation_sent = True
            invitation.save()
