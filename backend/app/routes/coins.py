from flask import Blueprint, jsonify, request
from backend.app.utils.api import fetch_coin_data
from backend.app.models import db, Coin, HistoricalData, CoinSnapshot
from datetime import datetime, timezone, timedelta

coins_bp = Blueprint('coins', __name__, url_prefix='/api')


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

    # Get filter parameters
    interval = request.args.get('interval', '1d')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Define time filter
    time_deltas = {
        '1h': timedelta(hours=1),
        '1d': timedelta(days=1),
        '1w': timedelta(weeks=1),
        '1m': timedelta(days=30)
    }

    if interval not in time_deltas:
        return jsonify({"error": "Invalid interval."}), 400

    start_time = datetime.now(timezone.utc) - time_deltas[interval]

    history_query = HistoricalData.query.filter(
        HistoricalData.coin_id == coin_id,
        HistoricalData.timestamp >= start_time).order_by(HistoricalData.timestamp.desc())

    paginated_history = history_query.paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        "coin_id": coin_id,
        "interval": interval,
        "page": page,
        "limit": limit,
        "total_pages": paginated_history.pages,
        "total_entries": paginated_history.total,
        "history": [
            {
                'price': h.price,
                'high': h.high,
                'low': h.low,
                'volume': h.volume,
                'timestamp': h.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for h in paginated_history.items
        ]
    })


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


@coins_bp.route('/coins/symbol/<symbol>', methods=['GET'])
def get_coin_by_symbol(symbol):
    coin = Coin.query.filter_by(coin_symbol=symbol.upper()).first()
    if not coin:
        return jsonify({"message": "Coin not found"}), 404

    latest_history = HistoricalData.query.filter_by(coin_id=coin.id)\
        .order_by(HistoricalData.timestamp.desc()).first()

    snapshot = CoinSnapshot.query.filter_by(coin_id=coin.id)\
        .order_by(CoinSnapshot.timestamp.desc()).first()

    return jsonify({
        "coin_name": coin.coin_name,
        "symbol": coin.coin_symbol,
        "image": coin.coin_image,
        "price": latest_history.price if latest_history else None,
        "high": latest_history.high if latest_history else None,
        "low": latest_history.low if latest_history else None,
        "market_cap": snapshot.market_cap if snapshot else None,
        "global_volume": snapshot.global_volume if snapshot else None,
        "description": coin.description
    })
