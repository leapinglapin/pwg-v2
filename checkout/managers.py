from django.db import models


class OpenCartManager(models.Manager):
    """For searching/creating OPEN carts only."""
    use_in_migrations = True
    status_filter = ["Open", "Frozen"]

    def get_queryset(self):
        return super().get_queryset().filter(
            status__in=self.status_filter, store_initiated_charge=False)

    def get_or_create(self, **kwargs):
        return self.get_queryset().get_or_create(
            status__in=self.status_filter, store_initiated_charge=False, **kwargs)


class SubmittedCartManager(models.Manager):
    """For searching/creating SUBMITTED carts only."""
    use_in_migrations = True
    # Delivered is in this list for legacy purposes, as there are a few floating around the db.
    status_filter = ["Submitted", "Paid", "Completed", "Shipped", "Cancelled", "Delivered"]

    def get_queryset(self):
        return super().get_queryset().filter(
            status__in=self.status_filter)

    def get_or_create(self, **kwargs):
        return self.get_queryset().get_or_create(
            status__in=self.status_filter, **kwargs)


class SavedCartManager(models.Manager):
    use_in_migrations = True
    """For searching/creating SAVED carts only."""
    status_filter = "Saved"

    def get_queryset(self):
        return super().get_queryset().filter(
            status=self.status_filter)

    def create(self, **kwargs):
        return self.get_queryset().create(status=self.status_filter, **kwargs)

    def get_or_create(self, **kwargs):
        return self.get_queryset().get_or_create(
            status=self.status_filter, **kwargs)
