"""
Cryptocurrency symbol mapping and normalization utilities.

Maps short coin symbols (BTC, ETH, etc.) to their Binance USDT trading pairs
and provides normalization functions for consistent symbol handling.
"""

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
    """
    Normalize cryptocurrency symbol to Binance USDT trading pair.

    Args:
        symbol: Short symbol (e.g., 'BTC') or full pair (e.g., 'BTCUSDT')

    Returns:
        str: Normalized Binance USDT trading pair symbol
    """
    return SYMBOL_MAP.get(symbol.upper(), symbol.upper())
