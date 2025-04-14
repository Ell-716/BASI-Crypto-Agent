from backend.app import db
from backend.app.models import HistoricalData, Coin
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone
from backend.app.models import TopVolume24h
from sqlalchemy import cast, Date


def update_top_volume_24h():
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    today = datetime.now(timezone.utc).date()

    # Delete existing entries for today
    db.session.query(TopVolume24h).filter(
        cast(TopVolume24h.timestamp, Date) == today
    ).delete()

    # Get summed volumes for each coin over the last 24h
    results = (
        db.session.query(
            Coin.id.label("coin_id"),
            func.sum(HistoricalData.volume).label("top_volume")
        )
        .join(HistoricalData, Coin.id == HistoricalData.coin_id)
        .filter(HistoricalData.timestamp >= since)
        .group_by(Coin.id)
        .all()
    )

    for row in results:
        db.session.add(TopVolume24h(
            coin_id=row.coin_id,
            top_volume=row.top_volume,
            timestamp=datetime.now(timezone.utc)
        ))

    db.session.commit()
    print(f"[TopVolume] Stored volume for {len(results)} coins.")


def get_top_coin_by_24h_volume():
    today = datetime.now(timezone.utc).date()

    result = (
        db.session.query(
            Coin.coin_name,
            Coin.coin_symbol,
            Coin.coin_image,
            TopVolume24h.top_volume
        )
        .join(TopVolume24h, Coin.id == TopVolume24h.coin_id)
        .filter(cast(TopVolume24h.timestamp, Date) == today)
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
