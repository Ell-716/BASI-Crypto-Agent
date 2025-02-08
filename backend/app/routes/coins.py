from flask import Blueprint, jsonify
import requests
from backend.app.models import db, Coin, HistoricalData
from datetime import datetime

coins_bp = Blueprint('coins', __name__, url_prefix='/api')

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"


@coins_bp.route('/add_coins', methods=['GET'])
def add_coins():
    try:
        response = requests.get(COINGECKO_API_URL, params={
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10
        })

        data = response.json()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    for coin in data:
        # Check if the coin exists in the database
        db_coin = Coin.query.filter_by(coin_symbol=coin['symbol']).first()
        if not db_coin:
            db_coin = Coin(
                coin_name=coin['name'],
                coin_symbol=coin['symbol'],
                coin_image=coin['image']
            )

            db.session.add(db_coin)
            db.session.commit()

        return jsonify({"message": "Coins added successfully."}), 200

