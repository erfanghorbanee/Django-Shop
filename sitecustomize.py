"""
Ensure the Django project directory (the folder containing manage.py: 'Django-Shop/')
is importable when running tools from the repository root, e.g., pytest.

Python automatically imports 'sitecustomize' if present on sys.path.
"""
import os
import sys

ROOT = os.path.dirname(__file__)
PROJECT_DIR = os.path.join(ROOT, "Django-Shop")
if os.path.isdir(PROJECT_DIR) and PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)