from backend.app.models import HistoricalData, Coin
from datetime import datetime, timezone, timedelta
from backend.app.prediction.prompt_formatter import generate_prompt, FULL_PROMPT_TEMPLATE, CONCISE_PROMPT_TEMPLATE
from groq import Groq
from dotenv import load_dotenv
import os
import logging
from backend.app.utils.llm_helpers import resample_and_compute_indicators
from backend.app.prediction.market_data import fetch_market_data
from backend.app.utils.symbols import SYMBOL_MAP


logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY')


def fetch_historical_data(coin_symbol, timeframe):
    """Fetch data from DB first, fall back to Binance only if DB is empty"""
    raw_symbol = coin_symbol.upper()
    normalized_symbol = SYMBOL_MAP.get(raw_symbol, raw_symbol)

    from flask import current_app

    with current_app.app_context():
        coin = Coin.query.filter_by(coin_symbol=raw_symbol).first()

        if not coin:
            print(f"[Prediction] Coin {raw_symbol} not found in DB")
            return None

        # Determine cutoff time based on timeframe
        if timeframe == "1h":
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=6)
        elif timeframe == "1w":
            cutoff_time = datetime.now(timezone.utc) - timedelta(weeks=12)  # 12 weeks for weekly
        else:  # 1d
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=60)

        # Try to fetch from DB first
        historical_data = HistoricalData.query.filter(
            HistoricalData.coin_id == coin.id,
            HistoricalData.timestamp >= cutoff_time
        ).order_by(HistoricalData.timestamp.asc()).all()

        if historical_data and len(historical_data) > 10:
            # We have sufficient DB data, use it
            print(f"[Prediction] Using {len(historical_data)} DB records for {raw_symbol}")
            df = resample_and_compute_indicators(historical_data, timeframe)
        else:
            # DB is empty or insufficient, try Binance as fallback (may fail with 429)
            print(f"[Prediction] Insufficient DB data for {raw_symbol}, trying Binance fallback")
            try:
                interval = "1w" if timeframe == "1w" else ("1h" if timeframe == "1h" else "1d")
                binance_df = fetch_market_data(normalized_symbol, interval, limit=500)

                if binance_df is None or binance_df.empty:
                    print(f"[Prediction] Binance fetch failed for {raw_symbol}")
                    # If we have ANY DB data, use it even if not ideal
                    if historical_data:
                        print(f"[Prediction] Falling back to {len(historical_data)} DB records")
                        df = resample_and_compute_indicators(historical_data, timeframe)
                    else:
                        return None
                else:
                    binance_df = binance_df.reset_index().rename(columns={"Date": "timestamp"})
                    binance_df.rename(columns={
                        "Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close",
                        "Volume": "volume"
                    }, inplace=True)
                    df = resample_and_compute_indicators(binance_df, timeframe)
            except Exception as e:
                print(f"[Prediction] Binance error for {raw_symbol}: {e}")
                # If we have ANY DB data, use it even if not ideal
                if historical_data:
                    print(f"[Prediction] Falling back to {len(historical_data)} DB records")
                    df = resample_and_compute_indicators(historical_data, timeframe)
                else:
                    return None

    if df is None or df.empty:
        return None

    latest_row = df.iloc[-1]
    latest_data = {
        "timestamp": str(latest_row.name),
        "open": round(latest_row["open"], 2),
        "close": round(latest_row["close"], 2),
        "high": round(latest_row["high"], 2),
        "low": round(latest_row["low"], 2),
        "volume": round(latest_row["volume"], 2)
    }

    summary = {
        "average_price": round(df["close"].mean(), 2),
        "highest_price": round(df["high"].max(), 2),
        "lowest_price": round(df["low"].min(), 2),
        "total_volume": round(df["volume"].sum(), 2)
    }

    trend_indicators = {
        "SMA_50": round(latest_row["SMA_50"], 2),
        "SMA_200": round(latest_row["SMA_200"], 2),
        "EMA_50": round(latest_row["EMA_50"], 2),
        "EMA_200": round(latest_row["EMA_200"], 2)
    }

    momentum_indicators = {
        "MACD": round(latest_row["MACD"], 2),
        "MACD_signal": round(latest_row["MACD_Signal"], 2),
        "RSI": round(latest_row["RSI"], 2),
        "Stoch_RSI_K": round(latest_row["Stoch_RSI_K"], 2),
        "Stoch_RSI_D": round(latest_row["Stoch_RSI_D"], 2)
    }

    volatility = {
        "BB_upper": round(latest_row["BB_upper"], 2),
        "BB_middle": round(latest_row["BB_middle"], 2),
        "BB_lower": round(latest_row["BB_lower"], 2)
    }

    # Volatility flags
    if df["close"].std() < 0.0001:
        print(f"{coin.coin_symbol} has very low price volatility. MACD & BB may be unreliable.")
        momentum_indicators["MACD"], momentum_indicators["MACD_signal"] = None, None
        volatility["BB_upper"], volatility["BB_middle"], volatility["BB_lower"] = None, None, None

    if volatility["BB_middle"] is None:
        volatility_status = "Low"
    else:
        threshold = 0.01 if volatility["BB_middle"] > 5000 else 0.03
        diff = abs(volatility["BB_upper"] - volatility["BB_lower"]) / volatility["BB_middle"]
        volatility_status = "High" if diff > threshold else "Low"

    # S&R
    recent_window = df.tail(30) if len(df) >= 30 else df
    support_levels = [
        float(round(recent_window["low"].min() * 0.98, 2)),
        float(round(recent_window["low"].min() * 0.95, 2))
    ]
    resistance_levels = [
        float(round(recent_window["high"].max() * 1.02, 2)),
        float(round(recent_window["high"].max() * 1.05, 2))
    ]

    # Recommendation
    rsi = momentum_indicators["RSI"]
    if rsi > 70:
        recommendation = "**SELL**"
    elif rsi < 30:
        recommendation = "**BUY on retracement**"
    else:
        recommendation = "**HOLD**"

    return {
        "coin": coin_symbol.upper(),
        "timeframe": timeframe,
        "latest_data": latest_data,
        "aggregated_stats": summary,
        "trend_indicators": trend_indicators,
        "momentum_indicators": momentum_indicators,
        "volatility": volatility,
        "derived_observations": {
            "trend": "Bullish" if trend_indicators["SMA_50"] > trend_indicators["SMA_200"] else "Bearish",
            "volatility": volatility_status,
            "support_levels": support_levels,
            "resistance_levels": resistance_levels
        },
        "investment_recommendation": recommendation
    }


def analyze_with_llm(coin_symbol, timeframe, report_type="concise"):
    data = fetch_historical_data(coin_symbol, timeframe)
    if not data:
        return {"error": "No sufficient data available."}

    prompt = generate_prompt(data, report_type)

    try:
        client = Groq(api_key=API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": FULL_PROMPT_TEMPLATE if report_type == "full" else CONCISE_PROMPT_TEMPLATE},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500 if report_type == "full" else 500,
            temperature=0.2
        )
        return {
            "coin": coin_symbol.upper(),
            "analysis": response.choices[0].message.content
        }
    except Exception as e:
        return {"error": f"LLM call failed: {str(e)}"}

