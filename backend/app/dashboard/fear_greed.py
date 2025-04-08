import requests
from datetime import datetime

FNG_URL = "https://api.alternative.me/fng/"
cached_index = None
last_updated = None


def fetch_fear_and_greed_index():
    global cached_index, last_updated
    try:
        response = requests.get(FNG_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        latest = data['data'][0]
        cached_index = {
            "value": int(latest["value"]),
            "classification": latest["value_classification"],
            "timestamp": int(latest["timestamp"])
        }
        last_updated = datetime.utcnow()
        print(f"[FearGreed] Updated at {last_updated}")
        return cached_index
    except Exception as e:
        raise Exception(f"Error fetching Fear & Greed Index: {e}")


def get_cached_fear_and_greed_index():
    if not cached_index:
        # fallback: fetch immediately on first request
        return fetch_fear_and_greed_index()
    return cached_index
