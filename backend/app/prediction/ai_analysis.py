from backend.app import create_app
from backend.app.models import HistoricalData, TechnicalIndicators, Coin
from datetime import datetime, timezone, timedelta
from backend.app.prediction.prompt_formatter import generate_prompt, FULL_PROMPT_TEMPLATE, CONCISE_PROMPT_TEMPLATE
from groq import Groq
from dotenv import load_dotenv
import os
import logging
import pandas as pd


logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY')

# Initialize Flask app context
app = create_app()


def fetch_historical_data(coin_symbol, timeframe):
    """Retrieve summarized historical price data and indicators for a given coin and timeframe."""
    with app.app_context():
        coin = Coin.query.filter_by(coin_symbol=coin_symbol.upper()).first()
        if not coin:
            return None

        # Define timeframe mappings
        timeframes = {
            "1h": timedelta(hours=1),
            "1d": timedelta(days=1),
            "1w": timedelta(weeks=1),
            "1m": timedelta(weeks=4)
        }

        if timeframe not in timeframes:
            return None

        cutoff_time = datetime.now(timezone.utc) - timeframes[timeframe]

        # Fetch historical data
        historical_data = HistoricalData.query.filter(
            HistoricalData.coin_id == coin.id,
            HistoricalData.timestamp >= cutoff_time
        ).order_by(HistoricalData.timestamp.asc()).all()

        # Fetch latest indicators
        indicators = TechnicalIndicators.query.filter_by(coin_id=coin.id).first()

        if not historical_data or not indicators:
            return None

        # Extract latest historical data point
        latest_entry = historical_data[-1]
        latest_data = {
            "timestamp": str(latest_entry.timestamp),
            "open": latest_entry.price,
            "close": latest_entry.price,
            "high": latest_entry.high,
            "low": latest_entry.low,
            "volume": latest_entry.volume
        }

        # Compute summary statistics
        summary = {
            "average_price": round(sum(entry.price for entry in historical_data) / len(historical_data), 2),
            "highest_price": round(max(entry.high for entry in historical_data), 2),
            "lowest_price": round(min(entry.low for entry in historical_data), 2),
            "total_volume": round(sum(entry.volume for entry in historical_data), 2)
        }

        # Trend & momentum indicators
        trend_indicators = {
            "SMA_50": round(indicators.SMA_50, 2),
            "SMA_200": round(indicators.SMA_200, 2),
            "EMA_50": round(indicators.EMA_50, 2),
            "EMA_200": round(indicators.EMA_200, 2)
        }

        momentum_indicators = {
            "MACD": round(indicators.MACD, 2),
            "MACD_signal": round(indicators.MACD_Signal, 2),
            "RSI": round(indicators.RSI, 2),
            "Stoch_RSI_K": round(indicators.Stoch_RSI_K, 2),
            "Stoch_RSI_D": round(indicators.Stoch_RSI_D, 2)
        }

        volatility = {
            "BB_upper": round(indicators.BB_upper, 2),
            "BB_middle": round(indicators.BB_middle, 2),
            "BB_lower": round(indicators.BB_lower, 2)
        }

        # Detect Low Volatility
        price_std = pd.Series([entry.price for entry in historical_data]).std()
        if price_std < 0.0001:  # Price barely moves
            print(f"⚠️ {coin.coin_symbol} has very low price volatility. MACD & BB may be unreliable.")
            momentum_indicators["MACD"], momentum_indicators["MACD_signal"] = None, None
            volatility["BB_upper"], volatility["BB_middle"], volatility["BB_lower"] = None, None, None

        # Compute Volatility Status Safely
        if volatility["BB_middle"] is None:
            volatility_status = "Low"
        else:
            threshold = 0.01 if volatility["BB_middle"] > 5000 else 0.03
            volatility_status = "High" if abs(volatility["BB_upper"] - volatility["BB_lower"]) / volatility[
                "BB_middle"] > threshold else "Low"

        volatility_warning = ("⚠️ The market is experiencing low volatility. Some indicators "
                              "(MACD, Bollinger Bands) may be unreliable.") if volatility_status == "Low" else ""

        # Proper Support & Resistance Calculation
        lowest_price = summary["lowest_price"]
        highest_price = summary["highest_price"]

        support_levels = [round(lowest_price * 0.98, 2), round(lowest_price * 0.95, 2)]
        resistance_levels = [round(highest_price * 1.02, 2), round(highest_price * 1.05, 2)]

        # Investment recommendation
        if momentum_indicators["RSI"] > 70:
            investment_recommendation = "**SELL**"
        elif momentum_indicators["RSI"] < 30:
            investment_recommendation = "**BUY on retracement**"
        else:
            investment_recommendation = "**HOLD**"

        # Final JSON structure
        return {
            "coin": coin_symbol.upper(),
            "timeframe": timeframe,
            "latest_data": latest_data,
            "aggregated_stats": summary,
            "trend_indicators": trend_indicators,
            "momentum_indicators": momentum_indicators,
            "volatility": volatility,
            "derived_observations": {
                "trend": "Bullish" if indicators.SMA_50 > indicators.SMA_200 else "Bearish",
                "volatility": volatility_status,
                "volatility_warning": volatility_warning,
                "support_levels": support_levels,
                "resistance_levels": resistance_levels
            },
            "investment_recommendation": investment_recommendation
        }


def analyze_with_llm(coin_symbol, timeframe, report_type="concise"):
    """Analyze market data using LLM and return either a concise or full report."""
    data = fetch_historical_data(coin_symbol, timeframe)
    if not data:
        return {"error": "No sufficient data available."}

    # Generate the appropriate prompt
    prompt = generate_prompt(data, report_type)

    client = Groq(api_key=API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": FULL_PROMPT_TEMPLATE if report_type == "full" else CONCISE_PROMPT_TEMPLATE},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500 if report_type == "full" else 500
    )

    return {"coin": coin_symbol.upper(), "analysis": response.choices[0].message.content}
