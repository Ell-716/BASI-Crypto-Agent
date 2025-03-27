from flask import Blueprint, jsonify
from backend.app.dashboard.coin_data import get_live_top_10_coins

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route("/dashboard/coins", methods=["GET"])
def dashboard_top_10_coins():
    data = get_live_top_10_coins()
    return jsonify(data)

@dashboard_bp.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "route works"})
