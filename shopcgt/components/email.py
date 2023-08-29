import os

from dotenv import load_dotenv

from shopcgt.components.ProjectPaths import ProjectPaths

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'admin@printedwargames.com'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS")
