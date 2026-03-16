"""
Top 24h trading volume tracker for cryptocurrency dashboard.

Calculates and stores the coin with highest 24-hour trading volume based on
historical data. Implements a 2-day rolling window for data cleanup.
"""
from backend.app import db
from backend.app.models import HistoricalData, Coin
from sqlalchemy import desc
from datetime import datetime, timedelta, timezone
from backend.app.models import TopVolume24h


def update_top_volume_24h():
    """
    Calculate and store 24-hour trading volume for all coins.

    Computes the total quote volume (price * volume) for each coin over the past
    24 hours using historical data. Implements a 2-day rolling window by deleting
    entries older than 2 days to prevent unbounded database growth.

    The function:
    1. Removes TopVolume24h entries older than 2 days
    2. For each coin, sums (price * volume) from all historical entries in the last 24h
    3. Stores the calculated volume with current timestamp in TopVolume24h table
    4. Logs cleanup and storage statistics

    This data is used by the dashboard to display the coin with highest trading activity.

    Returns:
        None: Results are stored in the database and logged to console.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=2)
    volume_window = now - timedelta(hours=24)

    # Delete entries older than 2 days
    old_entries = db.session.query(TopVolume24h).filter(
        TopVolume24h.timestamp < cutoff
    ).all()
    for entry in old_entries:
        db.session.delete(entry)
    db.session.commit()
    print(f"[TopVolume] Deleted {len(old_entries)} entries before {cutoff.date()}")

    coins = Coin.query.all()
    count = 0

    for coin in coins:
        historical_entries = (
            HistoricalData.query
            .filter(HistoricalData.coin_id == coin.id)
            .filter(HistoricalData.timestamp >= volume_window)
            .all()
        )

        if not historical_entries:
            continue

        total_quote_volume = sum(entry.price * entry.volume for entry in historical_entries)

        db.session.add(TopVolume24h(
            coin_id=coin.id,
            top_volume=total_quote_volume,
            timestamp=now
        ))
        count += 1

    db.session.commit()
    print(f"[TopVolume] Stored volume for {count} coins.")


def get_top_coin_by_24h_volume():
    """Get the coin with highest 24h volume. Returns most recent data if today's not available."""
    now = datetime.now(timezone.utc)
    # Make timezone-naive for DB comparison
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    tomorrow_start = today_start + timedelta(days=1)

    # Try to get today's data first
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

    # If no data for today, get the coin with highest volume from available data
    if not result:
        print("[TopVolume] No data for today, fetching highest volume entry")
        result = (
            db.session.query(
                Coin.coin_name,
                Coin.coin_symbol,
                Coin.coin_image,
                TopVolume24h.top_volume
            )
            .join(TopVolume24h, Coin.id == TopVolume24h.coin_id)
            .order_by(desc(TopVolume24h.top_volume))
            .first()
        )

    if not result:
        raise Exception("No top volume data found.")

    return {
        "image": result.coin_image,
        "coin_name": result.coin_name,
        "symbol": result.coin_symbol,
        "top_volume": result.top_volume
    }
