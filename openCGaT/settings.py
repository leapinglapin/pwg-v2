"""
This is a django-split-settings main file.
For more information read this:
https://github.com/sobolevn/django-split-settings
Default environment is `developement`.
To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""

from split_settings.tools import optional, include
import os
from dotenv import load_dotenv
from openCGaT.components.ProjectPaths import ProjectPaths

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))
ENV = os.environ.get('DJANGO_ENV') or 'development'
print(ENV)
base_settings = [
    'base.py',
    'components/*.py',
    # Select the right env:
    optional('environments/{0}/*.py'.format(ENV)),
    # Optionally override some settings:
    optional('environments/local.py'),
]

# Include settings:
include(*base_settings)
