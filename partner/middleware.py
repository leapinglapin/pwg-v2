from django.http.request import split_domain_port
from django.utils.deprecation import MiddlewareMixin

from .models import *


class CurrentSiteDynamicMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.site = get_site(request)


SITE_CACHE = {}


def get_site(request):
    from django.conf import settings
    try:
        if request:
            site = _get_site_by_request(request)
            if site:
                return site
    except Exception:
        pass
    if getattr(settings, 'SITE_ID', ''):
        site_id = settings.SITE_ID
        return _get_site_by_id(site_id)


def _get_site_by_id(site_id):
    if site_id not in SITE_CACHE:
        site = Site.objects.get(pk=site_id)
        SITE_CACHE[site_id] = site
    return SITE_CACHE[site_id]


def _get_site_by_request(request):
    host = request.get_host()
    if host.startswith('www.'):  # Strip www subdomain.
        host = host[4:]
    try:
        # First attempt to look up the site by host with or without port.
        if host not in SITE_CACHE:
            SITE_CACHE[host] = Site.objects.get(domain__iexact=host)
        return SITE_CACHE[host]
    except Site.DoesNotExist:
        # Fallback to looking up site after stripping port from the host.
        domain, port = split_domain_port(host)
        if domain not in SITE_CACHE:
            SITE_CACHE[domain] = Site.objects.get(domain__iexact=domain)
        return SITE_CACHE[domain]


def get_by_natural_key(self, domain):
    return self.get(domain=domain)
