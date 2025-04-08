import requests

BINANCE_BASE_URL = "https://api.binance.com"

# Define the top 10 coins manually and use CoinGecko's CDN for images
TOP_10_BINANCE_COINS = [
    {"symbol": "BTCUSDT", "name": "Bitcoin",
     "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"},
    {"symbol": "ETHUSDT", "name": "Ethereum",
     "image": "https://assets.coingecko.com/coins/images/279/large/ethereum.png"},
    {"symbol": "BNBUSDT", "name": "BNB", "image": "https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png"},
    {"symbol": "SOLUSDT", "name": "Solana", "image": "https://assets.coingecko.com/coins/images/4128/large/solana.png"},
    {"symbol": "XRPUSDT", "name": "XRP",
     "image": "https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png"},
    {"symbol": "ADAUSDT", "name": "Cardano",
     "image": "https://assets.coingecko.com/coins/images/975/large/cardano.png"},
    {"symbol": "AVAXUSDT", "name": "Avalanche",
     "image": "https://assets.coingecko.com/coins/images/12559/large/coin-round-red.png"},
    {"symbol": "DOGEUSDT", "name": "Dogecoin",
     "image": "https://assets.coingecko.com/coins/images/5/large/dogecoin.png"},
    {"symbol": "DOTUSDT", "name": "Polkadot",
     "image": "https://assets.coingecko.com/coins/images/12171/large/polkadot.png"},
    {"symbol": "LINKUSDT", "name": "Chainlink",
     "image": "https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png"},
]


def fetch_coin_data(coin_id=None):
    coins = []

    for coin in TOP_10_BINANCE_COINS:
        if coin_id and coin_id.lower() not in coin["name"].lower():
            continue

        try:
            res = requests.get(
                f"{BINANCE_BASE_URL}/api/v3/ticker/24hr",
                params={"symbol": coin["symbol"]},
                timeout=10
            )
            if res.status_code != 200:
                return [], f"Binance API error {res.status_code}: {res.text}"
            data = res.json()
            coins.append({
                "symbol": coin["symbol"].replace("USDT", ""),
                "name": coin["name"],
                "image": coin["image"],
                "current_price": float(data.get("lastPrice", 0)),
                "total_volume": float(data.get("volume", 0)),
                "market_cap": float(data.get("quoteVolume", 0)),  # approximation
                "high_24h": float(data.get("highPrice", 0)),
                "low_24h": float(data.get("lowPrice", 0)),
            })
        except requests.exceptions.RequestException as e:
            return [], str(e)
        except (ValueError, KeyError) as e:
            return [], f"Invalid response for {coin['symbol']}: {e}"

    return coins, None
