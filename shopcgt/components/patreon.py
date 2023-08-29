import os
from dotenv import load_dotenv
from shopcgt.components.ProjectPaths import ProjectPaths

from shopcgt.base import INSTALLED_APPS, AUTHENTICATION_BACKENDS

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

INSTALLED_APPS += (
    # The following apps are required:
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers you want to enable:
    'allauth.socialaccount.providers.patreon',
)
AUTHENTICATION_BACKENDS += (
    'allauth.account.auth_backends.AuthenticationBackend',
)

PATREON_CLIENT_ID = os.getenv('PATREON_CLIENT_ID')
PATREON_CLIENT_SECRET = os.getenv('PATREON_CLIENT_SECRET')
# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'patreon': {
        'VERIFIED_EMAIL': True,

        'VERSION': 'v2',
        'SCOPE': ['identity', 'identity[email]', 'campaigns', 'campaigns.members'],

    }
}

ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# Setting this hopefully means logins will redirect to the page the user was on
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
