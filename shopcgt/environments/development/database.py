import os
from dotenv import load_dotenv
from shopcgt.components.ProjectPaths import ProjectPaths
load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("PSQL_DATABASE", default='cgt_db'),
        'USER': "cgt",
        'PASSWORD': "cgt",
        'HOST': os.getenv("PSQL_HOST"),
        'PORT': os.getenv("PSQL_PORT"),
    }
}
