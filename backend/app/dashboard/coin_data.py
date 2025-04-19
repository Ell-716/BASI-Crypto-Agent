from backend.app.models import HistoricalData, Coin
from sqlalchemy import desc


def get_cached_top_10_coins():
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
