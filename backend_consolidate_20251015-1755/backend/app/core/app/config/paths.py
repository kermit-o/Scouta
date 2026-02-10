import sys
import os

def setup_paths():
    """Setup Python paths for the application"""
    app_dir = os.path.dirname(os.path.dirname(__file__))
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    print(f"Python paths setup: {sys.path}")
