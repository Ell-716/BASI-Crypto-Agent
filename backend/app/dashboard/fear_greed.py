import requests
from datetime import datetime
from backend.app.models import db, FearGreedIndex

FNG_URL = "https://api.alternative.me/fng/"


def fetch_fear_and_greed_index():
    try:
        response = requests.get(FNG_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        latest = data['data'][0]

        value = int(latest["value"])
        classification = latest["value_classification"]
        timestamp = datetime.fromtimestamp(int(latest["timestamp"]))

        db.session.query(FearGreedIndex).delete()

        index_entry = FearGreedIndex(
            value=value,
            classification=classification,
            timestamp=timestamp
        )
        db.session.add(index_entry)
        db.session.commit()
        print(f"[FearGreed] Stored new index: {value} ({classification}) at {timestamp}")

        return {
            "value": value,
            "classification": classification,
            "timestamp": int(latest["timestamp"])
        }

    except Exception as e:
        raise Exception(f"Error fetching Fear & Greed Index: {e}")
