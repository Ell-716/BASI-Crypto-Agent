import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app import create_app
from backend.app.dashboard.top_volume import update_top_volume_24h

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        update_top_volume_24h()
