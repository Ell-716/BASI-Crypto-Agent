from backend.app import create_app
from backend.app import socketio
import os

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

print(f"[INIT] Flask app initialized in {config_name} mode")

# Automatic backfill check
from backend.app.models import CoinPrice
with app.app_context():
    if CoinPrice.query.count() == 0:
        print("[INIT] No data found, running backfill...")
        from backfill import backfill_historical_data, seed_descriptions
        backfill_historical_data()
        seed_descriptions()
        print("[INIT] Backfill complete.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    socketio.run(app, host="0.0.0.0", port=port, debug=False, use_reloader=False)
