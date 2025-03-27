import requests

FNG_URL = "https://api.alternative.me/fng/"


def fetch_fear_and_greed_index():
    try:
        response = requests.get(FNG_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        latest = data['data'][0]
        return {
            "value": int(latest["value"]),
            "classification": latest["value_classification"],
            "timestamp": int(latest["timestamp"])
        }
    except Exception as e:
        raise Exception(f"Error fetching Fear & Greed Index: {e}")
