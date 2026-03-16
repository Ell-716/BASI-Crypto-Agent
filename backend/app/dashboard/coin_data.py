"""
Coin data retrieval for dashboard display.

Provides cached access to top cryptocurrency data from the database,
optimized for dashboard widgets that display current market leaders.
"""
from backend.app.models import HistoricalData, Coin
from sqlalchemy import desc


def get_cached_top_10_coins():
    """
    Retrieve top 10 cryptocurrencies from the latest historical data snapshot.

    Queries the database for the most recent historical data timestamp and returns
    the top 10 coins ordered by price. Uses database caching to avoid expensive
    real-time API calls.

    Returns:
        list[dict]: List of dictionaries containing coin data with keys:
            - name (str): Full coin name
            - symbol (str): Trading symbol
            - image (str): URL to coin icon/logo
            - price (float): Current price, rounded to 2 decimals
            - high_24h (float): 24-hour high price, rounded to 2 decimals
            - low_24h (float): 24-hour low price, rounded to 2 decimals
    """
    latest_time = HistoricalData.query.order_by(desc(HistoricalData.timestamp)).first().timestamp

    data = (
        HistoricalData.query
        .filter(HistoricalData.timestamp == latest_time)
        .join(Coin)
        .with_entities(
            Coin.coin_name,
            Coin.coin_symbol,
            Coin.coin_image,
            HistoricalData.price,
            HistoricalData.high_24h,
            HistoricalData.low_24h
        )
        .order_by(desc(HistoricalData.price))
        .limit(10)
        .all()
    )

    return [
        {
            "name": name,
            "symbol": symbol,
            "image": image,
            "price": round(price, 2),
            "high_24h": round(high_24h, 2),
            "low_24h": round(low_24h, 2),
        }
        for name, symbol, image, price, high_24h, low_24h in data
    ]
