import os
from dotenv import load_dotenv
from openCGaT.components.ProjectPaths import ProjectPaths
load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

# SECURITY WARNING: This key is only used in dev. Production has its own key imported from .env files
SECRET_KEY = "FDJKLREJKLREWJKLR:JEKL:*ERJKWRJEKLRJELTJHFDKLNLER:Y*&AQW"
