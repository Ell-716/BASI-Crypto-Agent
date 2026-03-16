"""
Dashboard API routes for cryptocurrency market data.

Provides endpoints for top coins, fear & greed index, trading volume leaders,
price sparklines, and coin snapshots.
"""
from flask import Blueprint, jsonify
from backend.app.dashboard.coin_data import get_cached_top_10_coins
from backend.app.models import FearGreedIndex
from backend.app.dashboard.top_volume import get_top_coin_by_24h_volume
from backend.app.models import Coin, HistoricalData, CoinSnapshot
from datetime import datetime, timedelta, timezone

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route("/dashboard/coins", methods=["GET"])
def dashboard_top_10_coins():
    """Get top 10 cryptocurrencies with current market data."""
    data = get_cached_top_10_coins()
    return jsonify(data)


@dashboard_bp.route("/dashboard/fear-greed", methods=["GET"])
def dashboard_fear_greed():
    """
    Retrieve latest Fear & Greed Index value.

    Endpoint: GET /dashboard/fear-greed

    Returns the most recent Fear & Greed Index reading, which measures
    market sentiment on a scale of 0-100. Used by the dashboard to display
    current market psychology (Extreme Fear to Extreme Greed).

    Returns:
        Response: JSON object with value, classification, and timestamp (200),
                 not found error (404) if no data, or server error (500)
    """
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
    """
    Get cryptocurrency with highest 24-hour trading volume.

    Endpoint: GET /dashboard/top-volume

    Identifies and returns the coin with the highest trading activity over
    the past 24 hours. Used by the dashboard to highlight the most actively
    traded cryptocurrency.

    Returns:
        Response: JSON object with coin image, name, symbol, and top_volume (200),
                 or server error (500) if calculation fails
    """
    try:
        coin = get_top_coin_by_24h_volume()
        return jsonify(coin)
    except Exception as e:
        print(f"[Dashboard] Top volume error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/dashboard/sparkline/<symbol>", methods=["GET"])
def get_sparkline_data(symbol):
    """
    Retrieve 7-day price history for sparkline chart.

    Endpoint: GET /dashboard/sparkline/<symbol>

    Fetches the past 7 days of price data for the specified coin, used to
    render small inline price trend charts (sparklines) on the dashboard
    and coin detail pages.

    Args:
        symbol (str): Cryptocurrency trading symbol

    Returns:
        Response: JSON array of price values rounded to 4 decimals (200),
                 not found error (404) if coin doesn't exist,
                 or server error (500)
    """
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


@dashboard_bp.route("/dashboard/snapshot/<symbol>", methods=["GET"])
def get_latest_snapshot(symbol):
    """
    Get latest market snapshot for a specific coin.

    Endpoint: GET /dashboard/snapshot/<symbol>

    Retrieves the most recent market data snapshot including market cap and
    global trading volume. Snapshots are updated periodically via cron jobs
    and provide aggregated market metrics.

    Args:
        symbol (str): Cryptocurrency trading symbol (case-insensitive)

    Returns:
        Response: JSON object with symbol, market_cap, global_volume, and timestamp (200),
                 or not found error (404) if coin or snapshot data unavailable
    """
    coin = Coin.query.filter_by(coin_symbol=symbol.upper()).first()
    if not coin:
        return jsonify({"error": "Coin not found"}), 404

    snapshot = (
        CoinSnapshot.query
        .filter_by(coin_id=coin.id)
        .order_by(CoinSnapshot.timestamp.desc())
        .first()
    )

    if not snapshot:
        return jsonify({"error": "No snapshot data available"}), 404

    return jsonify({
        "symbol": coin.coin_symbol,
        "market_cap": snapshot.market_cap,
        "global_volume": snapshot.global_volume,
        "timestamp": snapshot.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })
