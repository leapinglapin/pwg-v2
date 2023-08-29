import os
from dotenv import load_dotenv
from shopcgt.components.ProjectPaths import ProjectPaths

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

PRINTNODE_API_KEY = os.getenv("PRINTNODE")