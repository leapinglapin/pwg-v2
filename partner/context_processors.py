from django.conf import settings

from partner.middleware import get_site


def site(request):
    try:
        return {'site': get_site(request)}
    except Exception:
        return {}
