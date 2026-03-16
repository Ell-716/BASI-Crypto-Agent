"""
Chart generation routes for cryptocurrency technical analysis.

Provides endpoints to generate price charts, MACD/RSI charts, and Bollinger Bands
visualization as PNG images.
"""
from flask import Blueprint, send_file, request
from io import BytesIO
from backend.app.prediction.market_data import fetch_market_data, calculate_indicators
from backend.app.prediction.charts import plot_price_chart, plot_macd_rsi, plot_bollinger_bands
from backend.app.utils.chart_helpers import aggregate_candles

chart_bp = Blueprint("chart", __name__)


def render_chart(fig):
    """Convert matplotlib figure to PNG and return as Flask response."""
    output = BytesIO()
    fig.savefig(output, format="png", bbox_inches='tight')
    output.seek(0)
    return send_file(output, mimetype="image/png")


@chart_bp.route("/chart/price/<symbol>")
def price_chart(symbol):
    """
    Generate price candlestick chart with SMA overlays.

    Endpoint: GET /chart/price/<symbol>?timeframe=1h|1d|1w

    Creates a trading chart showing candlesticks, volume, support/resistance,
    and moving averages (SMA 50 and SMA 200). Used in AI prediction reports
    to display price action and trend direction.

    Args:
        symbol (str): Cryptocurrency trading symbol (e.g., 'BTC', 'ETH')

    Query Parameters:
        timeframe (str, optional): Candle aggregation period. Default '1d'.
                                  Options: '1h', '1d', '1w'

    Returns:
        Response: PNG image (image/png) on success, or 404 error if no data available
    """
    timeframe = request.args.get("timeframe", "1d")
    df_raw = fetch_market_data(symbol, timeframe)
    if df_raw is None or df_raw.empty:
        return "No data available", 404

    df = aggregate_candles(df_raw, timeframe)
    if df is None or df.empty:
        return "Not enough candles", 404

    df = calculate_indicators(df)
    fig = plot_price_chart(df, symbol, timeframe)
    return render_chart(fig)


@chart_bp.route("/chart/macd-rsi/<symbol>")
def macd_rsi_chart(symbol):
    """
    Generate MACD and Stochastic RSI indicator chart.

    Endpoint: GET /chart/macd-rsi/<symbol>?timeframe=1h|1d|1w

    Creates a dual-panel technical indicator chart with MACD (top) and
    Stochastic RSI (bottom). Used in AI prediction reports to identify
    momentum shifts, divergences, and overbought/oversold conditions.

    Args:
        symbol (str): Cryptocurrency trading symbol (e.g., 'BTC', 'ETH')

    Query Parameters:
        timeframe (str, optional): Candle aggregation period. Default '1d'.
                                  Options: '1h', '1d', '1w'

    Returns:
        Response: PNG image (image/png) on success, or 404 error if no data available
    """
    timeframe = request.args.get("timeframe", "1d")
    df_raw = fetch_market_data(symbol, timeframe)
    if df_raw is None or df_raw.empty:
        return "No data available", 404

    df = aggregate_candles(df_raw, timeframe)
    if df is None or df.empty:
        return "Not enough candles", 404

    df = calculate_indicators(df)
    fig = plot_macd_rsi(df, timeframe)
    return render_chart(fig)


@chart_bp.route("/chart/bollinger/<symbol>")
def bollinger_chart(symbol):
    """
    Generate price chart with Bollinger Bands overlay.

    Endpoint: GET /chart/bollinger/<symbol>?timeframe=1h|1d|1w

    Creates a candlestick chart with Bollinger Bands showing volatility bands
    calculated from 20-period SMA and 2 standard deviations. Used in AI prediction
    reports to identify overbought/oversold conditions and potential breakouts.

    Args:
        symbol (str): Cryptocurrency trading symbol (e.g., 'BTC', 'ETH')

    Query Parameters:
        timeframe (str, optional): Candle aggregation period. Default '1d'.
                                  Options: '1h', '1d', '1w'

    Returns:
        Response: PNG image (image/png) on success, or 404 error if no data available
    """
    timeframe = request.args.get("timeframe", "1d")
    df_raw = fetch_market_data(symbol, timeframe)
    if df_raw is None or df_raw.empty:
        return "No data available", 404

    df = aggregate_candles(df_raw, timeframe)
    if df is None or df.empty:
        return "Not enough candles", 404

    df = calculate_indicators(df)
    fig = plot_bollinger_bands(df, symbol, timeframe)
    return render_chart(fig)
