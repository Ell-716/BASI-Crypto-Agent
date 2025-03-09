from backend.app import create_app
from backend.app.models import HistoricalData, TechnicalIndicators, Coin
from datetime import datetime, timezone, timedelta
from backend.app.prediction.prompt_formatter import generate_prompt, FULL_PROMPT_TEMPLATE, CONCISE_PROMPT_TEMPLATE
from groq import Groq
from dotenv import load_dotenv
import os
import logging


logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY')

# Initialize Flask app context
app = create_app()


def fetch_historical_data(coin_symbol, timeframe):
    """Retrieve summarized historical price data and indicators for a given coin and timeframe."""
    with ((app.app_context())):
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
            "average_price": sum(entry.price for entry in historical_data) / len(historical_data),
            "highest_price": max(entry.high for entry in historical_data),
            "lowest_price": min(entry.low for entry in historical_data),
            "total_volume": sum(entry.volume for entry in historical_data)
        }

        # Trend & momentum indicators
        trend_indicators = {
            "SMA_50": indicators.SMA_50,
            "SMA_200": indicators.SMA_200,
            "EMA_50": indicators.EMA_50,
            "EMA_200": indicators.EMA_200
        }

        momentum_indicators = {
            "MACD": indicators.MACD,
            "MACD_signal": indicators.MACD_Signal,
            "RSI": indicators.RSI,
            "Stoch_RSI_K": indicators.Stoch_RSI_K,
            "Stoch_RSI_D": indicators.Stoch_RSI_D
        }

        volatility = {
            "BB_upper": indicators.BB_upper,
            "BB_middle": indicators.BB_middle,
            "BB_lower": indicators.BB_lower
        }

        # Derived observations
        derived_observations = {
            "trend": "Bullish" if indicators.SMA_50 > indicators.SMA_200 else "Bearish",
            "volatility": "High" if abs(
                indicators.BB_upper - indicators.BB_lower) / indicators.BB_middle > 0.05 else "Low",
            "support_levels": [summary["lowest_price"] * 0.98, summary["lowest_price"] * 0.95],
            "resistance_levels": [summary["highest_price"] * 1.02, summary["highest_price"] * 1.05]
        }

        # Investment recommendation
        investment_recommendation = "**HOLD**" if momentum_indicators["RSI"] > 40 else "**BUY on retracement**" if momentum_indicators["RSI"] < 30 else "**SELL**"

        # Final JSON structure
        return {
            "coin": coin_symbol.upper(),
            "timeframe": timeframe,
            "latest_data": latest_data,
            "aggregated_stats": summary,
            "trend_indicators": trend_indicators,
            "momentum_indicators": momentum_indicators,
            "volatility": volatility,
            "derived_observations": derived_observations,
            "short_term_analysis": "Short-term price movement is likely based on RSI and support levels.",
            "long_term_analysis": "Long-term trend remains bullish unless price breaks below key support.",
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
