import os
from dotenv import load_dotenv
from shopcgt.components.ProjectPaths import ProjectPaths

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

B2_ACCOUNT_ID = os.getenv('BACKBLAZE_ACCOUNT_ID')
B2_APP_KEY_ID = os.getenv('BACKBLAZE_APP_KEY_ID')
B2_APP_KEY = os.getenv('BACKBLAZE_APP_KEY')
B2_BUCKET_NAME = os.getenv('B2_BUCKET_NAME')
B2_BUCKET_ID = os.getenv('B2_BUCKET_ID')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
#STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
WHITENOISE_MANIFEST_STRICT = False


STATIC_ROOT = os.path.join(ProjectPaths.BASE_DIR, 'static/')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(ProjectPaths.PROJECT_ROOT, 'static'),
    os.path.join(ProjectPaths.BASE_DIR, 'tailwind/static')
]

MEDIA_ROOT = os.path.join(ProjectPaths.BASE_DIR, 'media')
MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'django_b2.storage.B2Storage'


AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER')
AZURE_PUBLIC_CONTAINER = os.getenv('AZURE_PUBLIC_CONTAINER')

AWS_ACCESS_KEY_ID = os.getenv('STATIC_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('STATIC_SECRET_KEY')

AWS_STORAGE_BUCKET_NAME = os.getenv('STATIC_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('STATIC_ENDPOINT_URL')

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'cgtstatic/static'
AWS_DEFAULT_ACL = 'public-read'