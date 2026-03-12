from flask import Blueprint, send_file, request
from io import BytesIO
import pandas as pd
from backend.app.prediction.market_data import calculate_indicators
from backend.app.prediction.charts import plot_price_chart, plot_macd_rsi, plot_bollinger_bands
from backend.app.utils.chart_helpers import aggregate_candles
from backend.app.models import Coin, HistoricalData

chart_bp = Blueprint("chart", __name__)


def render_chart(fig):
    output = BytesIO()
    fig.savefig(output, format="png", bbox_inches='tight')
    output.seek(0)
    return send_file(output, mimetype="image/png")


def fetch_historical_data_from_db(symbol):
    """Fetch historical data from database instead of Binance API"""
    # Get coin from database
    coin = Coin.query.filter_by(coin_symbol=symbol.upper()).first()
    if not coin:
        print(f"[Chart] Coin {symbol} not found in database")
        return None

    # Query historical data, ordered by timestamp
    historical_records = (
        HistoricalData.query
        .filter_by(coin_id=coin.id)
        .order_by(HistoricalData.timestamp.asc())
        .all()
    )

    if not historical_records:
        print(f"[Chart] No historical data for {symbol}")
        return None

    # Build DataFrame from database records
    data = []
    for record in historical_records:
        data.append({
            "Date": record.timestamp,
            "Open": record.price,  # Use price as Open (we don't store Open separately)
            "High": record.high if record.high else record.price,
            "Low": record.low if record.low else record.price,
            "Close": record.price,
            "Volume": record.volume
        })

    df = pd.DataFrame(data)
    df.set_index("Date", inplace=True)
    df = df.astype(float)

    print(f"[Chart] Loaded {len(df)} rows from database for {symbol}")
    return df


@chart_bp.route("/chart/price/<symbol>")
def price_chart(symbol):
    timeframe = request.args.get("timeframe", "1d")
    print(f"[Chart] Fetching price chart for {symbol} with timeframe {timeframe}")

    # Fetch from database instead of Binance
    df_raw = fetch_historical_data_from_db(symbol)
    if df_raw is None or df_raw.empty:
        print(f"[Chart] No historical data available for {symbol}")
        return "No data available", 404

    df = aggregate_candles(df_raw, timeframe)
    if df is None or df.empty:
        print(f"[Chart] Not enough candles after aggregation for {symbol}")
        return "Not enough candles", 404

    df = calculate_indicators(df)
    fig = plot_price_chart(df, symbol, timeframe)
    return render_chart(fig)


@chart_bp.route("/chart/macd-rsi/<symbol>")
def macd_rsi_chart(symbol):
    timeframe = request.args.get("timeframe", "1d")
    print(f"[Chart] Fetching MACD/RSI chart for {symbol} with timeframe {timeframe}")

    # Fetch from database instead of Binance
    df_raw = fetch_historical_data_from_db(symbol)
    if df_raw is None or df_raw.empty:
        print(f"[Chart] No historical data available for {symbol}")
        return "No data available", 404

    df = aggregate_candles(df_raw, timeframe)
    if df is None or df.empty:
        print(f"[Chart] Not enough candles after aggregation for {symbol}")
        return "Not enough candles", 404

    df = calculate_indicators(df)
    fig = plot_macd_rsi(df, timeframe)
    return render_chart(fig)


@chart_bp.route("/chart/bollinger/<symbol>")
def bollinger_chart(symbol):
    timeframe = request.args.get("timeframe", "1d")
    print(f"[Chart] Fetching Bollinger chart for {symbol} with timeframe {timeframe}")

    # Fetch from database instead of Binance
    df_raw = fetch_historical_data_from_db(symbol)
    if df_raw is None or df_raw.empty:
        print(f"[Chart] No historical data available for {symbol}")
        return "No data available", 404

    df = aggregate_candles(df_raw, timeframe)
    if df is None or df.empty:
        print(f"[Chart] Not enough candles after aggregation for {symbol}")
        return "Not enough candles", 404

    df = calculate_indicators(df)
    fig = plot_bollinger_bands(df, symbol, timeframe)
    return render_chart(fig)
