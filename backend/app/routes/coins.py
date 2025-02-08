from flask import Blueprint, jsonify
import requests
from backend.app.models import db, Coin, HistoricalData
from datetime import datetime, timezone

coins_bp = Blueprint('coins', __name__, url_prefix='/api')

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"


def fetch_coin_data():
    try:
        response = requests.get(COINGECKO_API_URL, params={
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10
        })
        return response.json(), None
    except Exception as e:
        return [], str(e)


@coins_bp.route('/add_coins', methods=['GET'])
def add_coins():
    data, error = fetch_coin_data()
    if error:
        return jsonify({"error": error}), 500

    new_coins = []

    for coin in data:
        # Check if coin already exists in the database
        db_coin = Coin.query.filter_by(coin_symbol=coin['symbol']).first()
        if not db_coin:
            new_coins.append(Coin(
                coin_name=coin['name'],
                coin_symbol=coin['symbol'],
                coin_image=coin['image']
            ))

    if new_coins:
        db.session.bulk_save_objects(new_coins)
        db.session.commit()

    return jsonify({"message": "Coins added successfully."}), 200


@coins_bp.route('/historical_data', methods=['GET'])
def get_historical_data():
    data, error = fetch_coin_data()
    if error:
        return jsonify({"error": error}), 500

    historical_entries = []

    for coin in data:
        # Ensure coin exists before updating historical data
        db_coin = Coin.query.filter_by(coin_symbol=coin['symbol']).first()
        if db_coin:
            historical_entries.append(HistoricalData(
                coin_id=db_coin.id,
                price=coin['current_price'],
                high=coin['high_24h'],
                low=coin['low_24h'],
                volume=coin['total_volume'],
                market_cap=coin['market_cap'],
                timestamp=datetime.now(timezone.utc)
            ))

    if historical_entries:
        db.session.bulk_save_objects(historical_entries)
        db.session.commit()

    return jsonify({"message": "Historical data updated successfully."}), 200
