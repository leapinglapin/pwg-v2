"""
Django settings for shopcgt project on Heroku. For more info, see:
https://github.com/heroku/heroku-django-template

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

from dotenv import load_dotenv

from shopcgt.components.ProjectPaths import ProjectPaths

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

apps_to_install = [
    'partner.apps.PartnerConfig',
    'cgtinfo.apps.CgtinfoConfig',
    'shop.apps.ShopConfig',
    'patreonlink.apps.PatreonlinkConfig',
    'intake.apps.IntakerConfig',
    'squarelink.apps.SquarelinkConfig',
    'digitalitems.apps.DigitalitemsConfig',
    'checkout',
    'payments',
    'inventory_report',
    'discount_codes',
    'giveaway',
    'tokens',
    'subscriptions',
    'game_info',
    'posts',
    'events',
    'credit',
    'realaddress',
    'images',
    'userinfo',
    'user_list',
    'packs',
    'crowdfund',
    'financial',
    'billing',
    # ^ Our Apps
    # v Dependencies
    'django_extensions',
    'storages',
    'imagekit',
    'treewidget',
    'django_b2',
    'address',
    'djmoney',
    'corsheaders',
    'rest_framework',
    'jquery',
    'django_react_templatetags',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    'mathfilters',
    'polymorphic',
    'mptt',

    # add the wagtail CMS
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    "wagtail.contrib.modeladmin",
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'modelcluster',
    'taggit',

    'debug_toolbar',
    "template_profiler_panel",
]

try:
    INSTALLED_APPS += apps_to_install
except:
    INSTALLED_APPS = apps_to_install

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'partner.middleware.CurrentSiteDynamicMiddleware',
    'checkout.middleware.CartMiddleware',
    # site level redirects from wagtail
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'shopcgt.urls'
WAGTAIL_SITE_NAME = os.environ.get(
    'WAGTAIL_SITE_NAME', "Comics Games and Things")

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(ProjectPaths.BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'partner.context_processors.site',
                # `allauth` needs this from django
                'django.template.context_processors.request',
                'django_react_templatetags.context_processors.react_context_processor',
            ],
            'builtins': [
                'shop.templatetags.templatehelpers',
                'checkout.templatetags.cart_load_tags',
                'django_react_templatetags.templatetags.react',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'shopcgt.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost'
]

SITE_ID = 1  # Default Site ID

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
