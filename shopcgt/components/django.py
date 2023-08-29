import os
from dotenv import load_dotenv
from shopcgt.components.ProjectPaths import ProjectPaths
load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "pze(1ng6kuw#czj8-lr#z1q-+axysyam9&b18gd@#l9)2g1(#^"
