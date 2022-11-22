import os
from dotenv import load_dotenv
from openCGaT.components.ProjectPaths import ProjectPaths
load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

ADMINS = [('nsh', 'nsh@comicsgamesandthings.com')]

