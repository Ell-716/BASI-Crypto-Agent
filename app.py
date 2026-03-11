from backend.app import create_app
from backend.app import socketio
import os
from datetime import datetime, timedelta, timezone

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

print(f"[INIT] Flask app initialized in {config_name} mode")

# Automatic backfill check - runs on app initialization
from backend.app.models import HistoricalData, CoinSnapshot, TopVolume24h, FearGreedIndex
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import desc

with app.app_context():
    try:
        if HistoricalData.query.count() == 0:
            print("[INIT] No data found, running backfill...")
            from backfill import backfill_historical_data, seed_descriptions
            backfill_historical_data()
            seed_descriptions()
            print("[INIT] Backfill complete.")
    except ProgrammingError:
        # Table doesn't exist yet - migrations need to run first
        print("[INIT] Database tables not yet created. Run migrations first.")

# Startup data refresh for cold starts (Render free tier)
print("[STARTUP] Checking data freshness...")

with app.app_context():
    try:
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(hours=24)

        # 1. Check Historical Data freshness
        try:
            latest_historical = HistoricalData.query.order_by(desc(HistoricalData.timestamp)).first()
            if not latest_historical or latest_historical.timestamp < stale_threshold:
                if latest_historical:
                    print(f"[STARTUP] Historical data last updated: {latest_historical.timestamp} (stale)")
                else:
                    print("[STARTUP] Historical data table empty")
                print("[STARTUP] Refreshing historical data...")
                from backend.app.tasks import update_historical_data, update_technical_indicators
                update_historical_data()
                update_technical_indicators()
                print("[STARTUP] Historical data refresh complete.")
            else:
                print(f"[STARTUP] Historical data is fresh (last update: {latest_historical.timestamp})")
        except Exception as e:
            print(f"[STARTUP] Error checking/updating historical data: {e}")

        # 2. Check CoinSnapshot freshness
        try:
            latest_snapshot = CoinSnapshot.query.order_by(desc(CoinSnapshot.timestamp)).first()
            if not latest_snapshot or latest_snapshot.timestamp < stale_threshold:
                if latest_snapshot:
                    print(f"[STARTUP] CoinSnapshot last updated: {latest_snapshot.timestamp} (stale)")
                else:
                    print("[STARTUP] CoinSnapshot table empty, populating...")
                from backend.app.utils.coin_gecko import update_coin_snapshots
                update_coin_snapshots()
                print("[STARTUP] Snapshot update complete.")
            else:
                print(f"[STARTUP] CoinSnapshot is fresh (last update: {latest_snapshot.timestamp})")
        except Exception as e:
            print(f"[STARTUP] Error checking/updating coin snapshots: {e}")

        # 3. Check TopVolume freshness
        try:
            latest_volume = TopVolume24h.query.order_by(desc(TopVolume24h.timestamp)).first()
            if not latest_volume or latest_volume.timestamp < stale_threshold:
                if latest_volume:
                    print(f"[STARTUP] TopVolume last updated: {latest_volume.timestamp} (stale)")
                else:
                    print("[STARTUP] TopVolume table empty, populating...")
                from backend.app.dashboard.top_volume import update_top_volume_24h
                update_top_volume_24h()
                print("[STARTUP] Top volume update complete.")
            else:
                print(f"[STARTUP] TopVolume is fresh (last update: {latest_volume.timestamp})")
        except Exception as e:
            print(f"[STARTUP] Error checking/updating top volume: {e}")

        # 4. Check FearGreedIndex freshness
        try:
            latest_fgi = FearGreedIndex.query.order_by(desc(FearGreedIndex.timestamp)).first()
            if not latest_fgi or latest_fgi.timestamp < stale_threshold:
                if latest_fgi:
                    print(f"[STARTUP] FearGreedIndex last updated: {latest_fgi.timestamp} (stale)")
                else:
                    print("[STARTUP] FearGreedIndex table empty, populating...")
                from backend.app.dashboard.fear_greed import fetch_fear_and_greed_index
                fetch_fear_and_greed_index()
                print("[STARTUP] FGI update complete.")
            else:
                print(f"[STARTUP] FearGreedIndex is fresh (last update: {latest_fgi.timestamp})")
        except Exception as e:
            print(f"[STARTUP] Error checking/updating fear & greed index: {e}")

        print("[STARTUP] All data checks complete. App ready.")

    except ProgrammingError as e:
        print(f"[STARTUP] Database tables not ready yet: {e}")
    except Exception as e:
        print(f"[STARTUP] Unexpected error during data refresh: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    socketio.run(app, host="0.0.0.0", port=port, debug=False, use_reloader=False)
