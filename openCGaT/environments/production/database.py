import os
from dotenv import load_dotenv
from openCGaT.components.ProjectPaths import ProjectPaths
load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cgt_db',
        'USER': os.getenv("PSQL_USERNAME"),
        'PASSWORD': os.getenv("PSQL_PASSWORD"),
        'HOST': os.getenv("PSQL_HOST"),
        'PORT': os.getenv("PSQL_PORT"),
    }
}