"""
AI-powered cryptocurrency prediction routes.

Provides endpoints for generating LLM-based market analysis and price predictions
using technical indicators and historical data.
"""
from flask import Blueprint, request, jsonify
from backend.app.prediction.ai_analysis import analyze_with_llm

predictions_bp = Blueprint("predictions", __name__)


@predictions_bp.route("/predict", methods=["GET"])
def get_prediction():
    """
    Generate AI-powered market analysis for a cryptocurrency.

    Query parameters:
        coin: Symbol of the cryptocurrency (required)
        timeframe: Data timeframe (default: "1d")
        type: Report type - "concise" or "detailed" (default: "concise")

    Returns:
        JSON response with AI analysis or error message
    """
    coin = request.args.get("coin")
    timeframe = request.args.get("timeframe", "1d")
    report_type = request.args.get("type", "concise")

    if not coin:
        return jsonify({"error": "Coin parameter is required"}), 400

    try:
        result = analyze_with_llm(coin, timeframe, report_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
