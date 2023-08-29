"""shopcgt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from shop.views import account_summary
from django.conf import settings
from django.conf.urls.static import static

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
                  path('', include('cgtinfo.urls')),
                  path('', include('game_info.urls')),
                  path('accounts/orders/', include('checkout.urls-orders')),
                  path('accounts/profile/', account_summary, name="account_summary"),
                  path('accounts/profile/', include('digitalitems.urls-account')),
                  path('accounts/profile/', include('userinfo.urls-account')),
                  path('accounts/profile/', include('checkout.urls-account')),
                  path('accounts/', include('allauth.urls')),
                  path('shop/', include('shop.urls')),
                  path('download/', include('digitalitems.urls-download')),
                  path('admin/', admin.site.urls),
                  path('packs/', include('subscriptions.urls')),

                  path('partner/<slug:partner_slug>/intake/', include('intake.urls')),
                  path('partner/<slug:partner_slug>/subscription/', include('subscriptions.urls-partner')),
                  path('partner/<slug:partner_slug>/inv_report/', include('inventory_report.urls')),
                  path('partner/', include('user_list.urls-partner')),
                  # Handle slug in individual urls so we don't have issues
                  path('partner/<slug:partner_slug>/packs/', include('packs.urls-partner')),

                  path('partner/', include('partner.urls')),

                  path('cart/', include('checkout.urls-cart')),
                  path('checkout/', include('checkout.urls')),
                  path('giveaways/', include('giveaway.urls')),

                  re_path(r'^cms/', include(wagtailadmin_urls)),
                  re_path(r'^documents/', include(wagtaildocs_urls)),
                  re_path(r'', include(wagtail_urls)),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
