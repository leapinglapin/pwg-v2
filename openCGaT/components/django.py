import os
from dotenv import load_dotenv
from openCGaT.components.ProjectPaths import ProjectPaths
load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "FDJKLREJKLREWJKLR:JEKL:*ERJKWRJEKLRJELTJHFDKLNLER:Y*&AQW"
