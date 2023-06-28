from realaddress.abstract_models import (
    AbstractCountry, AbstractUserAddress)


class RealCountry(AbstractCountry):
    """
    This model is "RealCountry" to contrast with the countries from django-address
    """

    class Meta:
        app_label = "realaddress"


class UserAddress(AbstractUserAddress):
    class Meta:
        app_label = "realaddress"

