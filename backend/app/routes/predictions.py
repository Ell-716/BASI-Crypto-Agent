from flask import Blueprint, request, jsonify
from backend.app.prediction.ai_analysis import analyze_with_llm

predictions_bp = Blueprint("predictions", __name__)


@predictions_bp.route("/predict", methods=["GET"])
def get_prediction():
    coin = request.args.get("coin")
    timeframe = request.args.get("timeframe", "1d")
    report_type = request.args.get("type", "concise")  # "concise" or "full"

    if not coin:
        return jsonify({"error": "Coin parameter is required"}), 400

    result = analyze_with_llm(coin, timeframe, report_type)
    return jsonify(result)
