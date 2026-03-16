"""
Cron job script for updating cryptocurrency market cap and volume snapshots.

Scheduled task that fetches market cap and trading volume data from CoinGecko API
and stores snapshots in the database for dashboard display.
Runs once a day via cron.
"""
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
