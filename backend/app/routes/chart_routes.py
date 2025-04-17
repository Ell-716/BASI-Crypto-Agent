from flask import Blueprint, send_file, request
from io import BytesIO
from backend.app.prediction.market_data import fetch_market_data, calculate_indicators
from backend.app.prediction.charts import plot_price_chart, plot_macd_rsi, plot_bollinger_bands
from backend.app.utils.chart_helpers import aggregate_candles

chart_bp = Blueprint("chart", __name__)


def render_chart(fig):
    output = BytesIO()
    fig.savefig(output, format="png", bbox_inches='tight')
    output.seek(0)
    return send_file(output, mimetype="image/png")


@chart_bp.route("/chart/price/<symbol>")
def price_chart(symbol):
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
