from flask import Blueprint, jsonify
from backend.app.dashboard.coin_data import get_live_top_10_coins
from backend.app.models import FearGreedIndex
from backend.app.dashboard.top_volume import get_top_coin_by_24h_volume
from backend.app.models import Coin, HistoricalData
from datetime import datetime, timedelta, timezone

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route("/dashboard/coins", methods=["GET"])
def dashboard_top_10_coins():
    data = get_live_top_10_coins()
    return jsonify(data)


@dashboard_bp.route("/dashboard/fear-greed", methods=["GET"])
def dashboard_fear_greed():
    try:
        latest = (
            FearGreedIndex.query.order_by(FearGreedIndex.timestamp.desc())
            .limit(1)
            .first()
        )

        if not latest:
            return jsonify({"error": "No Fear & Greed data available"}), 404

        return jsonify({
            "value": latest.value,
            "classification": latest.classification,
            "timestamp": int(latest.timestamp.timestamp())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/dashboard/top-volume", methods=["GET"])
def dashboard_top_volume():
    try:
        coin = get_top_coin_by_24h_volume()
        return jsonify(coin)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/dashboard/sparkline/<symbol>", methods=["GET"])
def get_sparkline_data(symbol):
    try:
        since = datetime.now(timezone.utc) - timedelta(days=7)

        coin = Coin.query.filter_by(coin_symbol=symbol).first()
        if not coin:
            return jsonify({"error": "Coin not found"}), 404

        data = (
            HistoricalData.query
            .filter(HistoricalData.coin_id == coin.id, HistoricalData.timestamp >= since)
            .order_by(HistoricalData.timestamp.asc())
            .all()
        )

        prices = [round(d.price, 4) for d in data]
        return jsonify(prices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
