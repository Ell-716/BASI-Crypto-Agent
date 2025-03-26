SYMBOL_MAP = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "XRP": "XRPUSDT",
    "ADA": "ADAUSDT",
    "SOL": "SOLUSDT",
    "DOGE": "DOGEUSDT",
    "DOT": "DOTUSDT",
    "BNB": "BNBUSDT",
    "AVAX": "AVAXUSDT",
    "LINK": "LINKUSDT"
}


def normalize_symbol(symbol):
    return SYMBOL_MAP.get(symbol.upper(), symbol.upper())
