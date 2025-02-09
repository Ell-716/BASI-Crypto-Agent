from flask import Blueprint, jsonify, request
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


@coins_bp.route('/coins', methods=['GET'])
def get_all_coins():
    coins = Coin.query.all()
    return jsonify([
        {
            'id': coin.id,
            'name': coin.coin_name,
            'symbol': coin.coin_symbol,
            'image': coin.coin_image
        } for coin in coins
    ])


@coins_bp.route('/coins/<int:coin_id>', methods=['GET'])
def get_coin(coin_id):
    coin = Coin.query.get(coin_id)
    if not coin:
        return jsonify({"message": "Coin not found"}), 404
    return jsonify({
        'id': coin.id,
        'name': coin.coin_name,
        'symbol': coin.coin_symbol,
        'image': coin.coin_image
    })


@coins_bp.route('/coins/<int:coin_id>/history', methods=['GET'])
def get_history(coin_id):
    history = HistoricalData.query.filter_by(coin_id=coin_id).order_by(HistoricalData.timestamp.desc()).all()
    return jsonify([
        {
            'price': h.price,
            'high': h.high,
            'low': h.low,
            'volume': h.volume,
            'market_cap': h.market_cap,
            'timestamp': h.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for h in history
    ])


@coins_bp.route('coins/<int:coin_id>', methods=['PUT'])
def update_coin(coin_id):
    coin = Coin.query.get(coin_id)
    if not coin:
        return jsonify({"message": "Coin not found"}), 404

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid or missing JSON data"}), 400

    coin.coin_name = data.get('name', coin.coin_name)
    coin.coin_symbol = data.get('symbol', coin.coin_symbol)
    coin.coin_image = data.get('image', coin.coin_image)

    db.session.commit()
    return jsonify({"message": "Coin updated"})


@coins_bp.route('/coins/<int:coin_id>', methods=['DELETE'])
def delete_coin(coin_id):
    coin = Coin.query.get(coin_id)
    if not coin:
        return jsonify({"message": "Coin not found"}), 404

    HistoricalData.query.filter_by(coin_id=coin_id).delete()

    db.session.delete(coin)
    db.session.commit()
    return jsonify({"message": "Coin and its historical data deleted successfully"})
