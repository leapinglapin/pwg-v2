import os


class ProjectPaths:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_folder = os.path.expanduser(PROJECT_ROOT)  # adjust as appropriate
