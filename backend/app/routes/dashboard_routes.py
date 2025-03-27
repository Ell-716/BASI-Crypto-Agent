from flask import Blueprint, jsonify
from backend.app.dashboard.coin_data import get_live_top_10_coins
from backend.app.dashboard.fear_greed import fetch_fear_and_greed_index

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route("/dashboard/coins", methods=["GET"])
def dashboard_top_10_coins():
    data = get_live_top_10_coins()
    return jsonify(data)


@dashboard_bp.route("/dashboard/fear-greed", methods=["GET"])
def dashboard_fear_greed():
    try:
        data = fetch_fear_and_greed_index()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
