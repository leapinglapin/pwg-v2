import os

# WAGTAILADMIN_BASE_URL  # Todo set this to default url
WAGTAIL_SITE_NAME = os.environ.get(
    'WAGTAIL_SITE_NAME', "Comics Games and Things")
