from backend.app import db
from backend.app.models import HistoricalData, Coin
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone
from backend.app.models import TopVolume24h
from sqlalchemy import func, Date


def update_top_volume_24h():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=2)
    volume_window = now - timedelta(hours=24)

    # Delete anything older than 2 days
    db.session.query(TopVolume24h).filter(
        TopVolume24h.timestamp < cutoff
    ).delete()

    # Calculate 24h volume
    results = (
        db.session.query(
            Coin.id.label("coin_id"),
            func.sum(HistoricalData.volume).label("top_volume")
        )
        .join(HistoricalData, Coin.id == HistoricalData.coin_id)
        .filter(HistoricalData.timestamp >= volume_window)
        .group_by(Coin.id)
        .all()
    )

    for row in results:
        db.session.add(TopVolume24h(
            coin_id=row.coin_id,
            top_volume=row.top_volume,
            timestamp=now
        ))

    db.session.commit()
    print(f"[TopVolume] Stored volume for {len(results)} coins.")


def get_top_coin_by_24h_volume():
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    result = (
        db.session.query(
            Coin.coin_name,
            Coin.coin_symbol,
            Coin.coin_image,
            TopVolume24h.top_volume
        )
        .join(TopVolume24h, Coin.id == TopVolume24h.coin_id)
        .filter(TopVolume24h.timestamp >= today_start)
        .filter(TopVolume24h.timestamp < tomorrow_start)
        .order_by(desc(TopVolume24h.top_volume))
        .first()
    )

    if not result:
        raise Exception("No top volume data found for today.")

    return {
        "image": result.coin_image,
        "coin_name": result.coin_name,
        "symbol": result.coin_symbol,
        "top_volume": result.top_volume
    }
