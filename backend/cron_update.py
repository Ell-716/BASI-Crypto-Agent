import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app.tasks import update_historical_data, update_technical_indicators

if __name__ == "__main__":
    update_historical_data()
    update_technical_indicators()
