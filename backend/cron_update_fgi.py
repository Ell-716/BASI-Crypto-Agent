import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app import create_app
from backend.app.dashboard.fear_greed import fetch_fear_and_greed_index

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        fetch_fear_and_greed_index()
