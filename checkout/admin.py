from django.contrib import admin

# Register your models here.
from checkout.models import Cart, CheckoutLine, TaxRateCache


class SubmittedCartAdmin(admin.ModelAdmin):
    search_fields = ['status', 'owner__email', 'owner__username']

    def get_queryset(self, request):
        # use our manager, rather than the default one
        qs = self.model.submitted.get_queryset()

        # we need this from the superclass method
        ordering = self.ordering or ()  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


admin.site.register(Cart, SubmittedCartAdmin)
admin.site.register(CheckoutLine)


admin.site.register(TaxRateCache)