import os
from dotenv import load_dotenv
from openCGaT.components.ProjectPaths import ProjectPaths

from openCGaT.base import INSTALLED_APPS, AUTHENTICATION_BACKENDS

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

INSTALLED_APPS += (
    # The following apps are required:
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers you want to enable:
)
AUTHENTICATION_BACKENDS += (
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
}

ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# Setting this hopefully means logins will redirect to the page the user was on
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
