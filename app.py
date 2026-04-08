"""
Main Flask application entry point.

Initializes the Flask app with WebSocket support, runs automatic backfill
if database is empty, and performs startup data freshness checks to ensure
all dashboard data is current. Designed for deployment on platforms like
Render with cold-start resilience.
"""
from backend.app import create_app
from backend.app import socketio
import os
import time
from datetime import datetime, timedelta, timezone

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

print(f"[INIT] Flask app initialized in {config_name} mode")

# Automatic backfill check - runs on app initialization
from backend.app.models import HistoricalData, CoinSnapshot, TopVolume24h, FearGreedIndex
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy import desc

with app.app_context():
    try:
        if HistoricalData.query.count() == 0:
            print("[INIT] No data found, running backfill...")
            from backfill import backfill_historical_data, seed_descriptions
            backfill_historical_data()
            seed_descriptions()
            print("[INIT] Backfill complete.")
            # Wait to avoid CoinGecko rate limit (backfill calls seed_descriptions which hits CoinGecko)
            print("[INIT] Waiting 5 seconds to avoid CoinGecko rate limit...")
            time.sleep(5)
    except (ProgrammingError, OperationalError) as e:
        # Table doesn't exist yet - migrations need to run first
        print(f"[INIT] Database tables not yet created. Run 'flask db upgrade' first.")
        print(f"[INIT] Error details: {type(e).__name__}")

# Startup data refresh for cold starts (Render free tier)
print("[STARTUP] Checking data freshness...")

with app.app_context():
    now = datetime.now(timezone.utc)
    historical_stale_threshold = now - timedelta(hours=6)
    stale_threshold = now - timedelta(hours=24)

    # Helper to ensure timestamp is timezone-aware for comparison
    def make_aware(dt):
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    # 1. Check Historical Data freshness
    try:
        latest_historical = HistoricalData.query.order_by(desc(HistoricalData.timestamp)).first()
        latest_ts = make_aware(latest_historical.timestamp) if latest_historical else None
        if not latest_historical or latest_ts < historical_stale_threshold:
            if latest_historical:
                print(f"[STARTUP] Historical data last updated: {latest_ts} (stale)")
            else:
                print("[STARTUP] Historical data table empty")
            print("[STARTUP] Refreshing historical data (backfilling recent klines)...")
            from backend.app.tasks import backfill_recent_klines, update_historical_data, update_technical_indicators
            backfill_recent_klines()
            update_historical_data()
            update_technical_indicators()
            print("[STARTUP] Historical data refresh complete.")
        else:
            print(f"[STARTUP] Historical data is fresh (last update: {latest_ts})")
    except (ProgrammingError, OperationalError):
        print("[STARTUP] Tables not ready, skipping historical data check")
    except Exception as e:
        print(f"[STARTUP] Error checking/updating historical data: {e}")

    # 2. Check CoinSnapshot freshness
    try:
        latest_snapshot = CoinSnapshot.query.order_by(desc(CoinSnapshot.timestamp)).first()
        snapshot_ts = make_aware(latest_snapshot.timestamp) if latest_snapshot else None
        if not latest_snapshot or snapshot_ts < stale_threshold:
            if latest_snapshot:
                print(f"[STARTUP] CoinSnapshot last updated: {snapshot_ts} (stale)")
            else:
                print("[STARTUP] CoinSnapshot table empty, populating...")
            from backend.app.utils.coin_gecko import update_coin_snapshots
            update_coin_snapshots()
            print("[STARTUP] Snapshot update complete.")
        else:
            print(f"[STARTUP] CoinSnapshot is fresh (last update: {snapshot_ts})")
    except (ProgrammingError, OperationalError):
        print("[STARTUP] Tables not ready, skipping coin snapshot check")
    except Exception as e:
        print(f"[STARTUP] Error checking/updating coin snapshots: {e}")

    # 3. Check TopVolume freshness
    try:
        latest_volume = TopVolume24h.query.order_by(desc(TopVolume24h.timestamp)).first()
        volume_ts = make_aware(latest_volume.timestamp) if latest_volume else None
        if not latest_volume or volume_ts < stale_threshold:
            if latest_volume:
                print(f"[STARTUP] TopVolume last updated: {volume_ts} (stale)")
            else:
                print("[STARTUP] TopVolume table empty, populating...")
            from backend.app.dashboard.top_volume import update_top_volume_24h
            update_top_volume_24h()
            print("[STARTUP] Top volume update complete.")
        else:
            print(f"[STARTUP] TopVolume is fresh (last update: {volume_ts})")
    except (ProgrammingError, OperationalError):
        print("[STARTUP] Tables not ready, skipping top volume check")
    except Exception as e:
        print(f"[STARTUP] Error checking/updating top volume: {e}")

    # 4. Check FearGreedIndex freshness
    try:
        latest_fgi = FearGreedIndex.query.order_by(desc(FearGreedIndex.timestamp)).first()
        fgi_ts = make_aware(latest_fgi.timestamp) if latest_fgi else None
        if not latest_fgi or fgi_ts < stale_threshold:
            if latest_fgi:
                print(f"[STARTUP] FearGreedIndex last updated: {fgi_ts} (stale)")
            else:
                print("[STARTUP] FearGreedIndex table empty, populating...")
            from backend.app.dashboard.fear_greed import fetch_fear_and_greed_index
            fetch_fear_and_greed_index()
            print("[STARTUP] FGI update complete.")
        else:
            print(f"[STARTUP] FearGreedIndex is fresh (last update: {fgi_ts})")
    except (ProgrammingError, OperationalError):
        print("[STARTUP] Tables not ready, skipping fear & greed index check")
    except Exception as e:
        print(f"[STARTUP] Error checking/updating fear & greed index: {e}")

    # 5. Populate Binance ticker cache for WebSocket
    try:
        print("[STARTUP] Populating Binance ticker cache...")
        from backend.app.utils.api import get_cached_binance_tickers
        tickers = get_cached_binance_tickers()
        if tickers:
            print(f"[STARTUP] Binance ticker cache populated with {len(tickers)} tickers")
        else:
            print("[STARTUP] Warning: Binance ticker cache is empty")
    except Exception as e:
        print(f"[STARTUP] Error populating Binance cache: {e}")

    print("[STARTUP] All data checks complete. App ready.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    socketio.run(app, host="0.0.0.0", port=port, debug=False, use_reloader=False)
