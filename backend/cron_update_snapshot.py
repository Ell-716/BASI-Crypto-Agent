import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app import create_app
from backend.app.utils.coin_gecko import update_coin_snapshots

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        update_coin_snapshots()
