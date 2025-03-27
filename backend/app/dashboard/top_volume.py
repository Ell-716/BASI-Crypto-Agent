from backend.app import db
from backend.app.models import HistoricalData, Coin
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone


def get_top_coin_by_24h_volume():
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    result = (
        db.session.query(
            Coin.coin_name,
            Coin.coin_symbol,
            Coin.coin_image,
            func.sum(HistoricalData.volume).label("total_volume")
        )
        .join(HistoricalData, Coin.id == HistoricalData.coin_id)
        .filter(HistoricalData.timestamp >= since)
        .group_by(Coin.id)
        .order_by(desc("total_volume"))
        .first()
    )

    if not result:
        raise Exception("No data found")

    return {
        "image": result.coin_image,
        "coin_name": result.coin_name,
        "symbol": result.coin_symbol
    }
