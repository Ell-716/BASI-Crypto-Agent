import requests

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"


def fetch_coin_data(coin_id=None):
    """Fetch market data for a specific coin or the top 10 coins."""
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1,
        'sparkline': False
    }
    if coin_id:
        params['ids'] = coin_id

    try:
        response = requests.get(COINGECKO_API_URL, params=params, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        else:
            return [], f"Error {response.status_code}: {response.text}"

    except requests.exceptions.RequestException as e:
        return [], str(e)
