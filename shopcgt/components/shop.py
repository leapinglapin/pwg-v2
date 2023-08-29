import os

from dotenv import load_dotenv

from shopcgt.components.ProjectPaths import ProjectPaths

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

# TREEWIDGET_TREEOPTIONS = {
#     'core': {
#         'strings': {
#             'Expand': 'Expaand'
#         }
#     }
# }
