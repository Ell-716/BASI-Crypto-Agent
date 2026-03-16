"""
Cron job script for updating the Crypto Fear & Greed Index.

Scheduled task that fetches the latest Fear & Greed Index from Alternative.me API
and stores it in the database for dashboard display.
Runs once a day via cron.
"""
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
