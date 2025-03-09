from backend.app import create_app
from backend.app.models import HistoricalData, TechnicalIndicators, Coin
from datetime import datetime, timezone, timedelta
import json

# Initialize Flask app context
app = create_app()

# Define the prompt template
PROMPT_TEMPLATE = """
You are an expert financial analyst specializing in cryptocurrency markets. 
Your task is to analyze historical price data, technical indicators, and market sentiment to provide a structured investment report.

### Crypto Analysis Report
- **Coin:** {coin}  
- **Timeframe:** {timeframe}  

### Latest Market Data
- **Timestamp:** {latest_data[timestamp]}  
- **Open Price:** ${latest_data[open]:,.2f}  
- **Close Price:** ${latest_data[close]:,.2f}  
- **High Price:** ${latest_data[high]:,.2f}  
- **Low Price:** ${latest_data[low]:,.2f}  
- **Volume:** ${latest_data[volume]:,.0f}  

### Trend Indicators
- **SMA 50:** ${trend_indicators[SMA_50]:,.2f}  
- **SMA 200:** ${trend_indicators[SMA_200]:,.2f}  
- **EMA 50:** ${trend_indicators[EMA_50]:,.2f}  
- **EMA 200:** ${trend_indicators[EMA_200]:,.2f}  

### Momentum Indicators
- **MACD:** {momentum_indicators[MACD]:,.2f}  
- **MACD Signal:** {momentum_indicators[MACD_signal]:,.2f}  
- **RSI:** {momentum_indicators[RSI]:,.2f}  
- **Stoch RSI K:** {momentum_indicators[Stoch_RSI_K]:,.2f}  
- **Stoch RSI D:** {momentum_indicators[Stoch_RSI_D]:,.2f}  

### Volatility & Support/Resistance
- **Bollinger Bands:**  
  - Upper: ${volatility[BB_upper]:,.2f}  
  - Middle: ${volatility[BB_middle]:,.2f}  
  - Lower: ${volatility[BB_lower]:,.2f}  
- **Trend:** {derived_observations[trend]}  
- **Volatility Level:** {derived_observations[volatility]}  
- **Support Levels:** {derived_observations[support_levels]}  
- **Resistance Levels:** {derived_observations[resistance_levels]}  

### Market Analysis
Based on the above data, determine:
1. **Current Market Trend** – Bullish, Bearish, or Neutral.
2. **Momentum & RSI Analysis** – Is the market overbought or oversold?
3. **Short-Term & Long-Term Expectations** – Predict price movement.
4. **Support & Resistance** – Identify key levels.
5. **Investment Verdict** – Should investors **BUY, SELL, or HOLD**?

### **Final Verdict**
Provide a clear recommendation:
- 🔴 **SELL / WAIT** if the trend is bearish.
- 🟡 **HOLD** if the market is uncertain.
- 🟢 **BUY** if the trend is bullish and indicators confirm a good entry.

**⚠ Disclaimer:** This analysis is for informational purposes only and should not be considered financial advice. Always conduct your own research before making investment decisions.
"""


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

        # Final JSON structure
        return json.dumps({
            "coin": coin_symbol.upper(),
            "timeframe": timeframe,
            "latest_data": latest_data,
            "aggregated_stats": summary,
            "trend_indicators": trend_indicators,
            "momentum_indicators": momentum_indicators,
            "volatility": volatility,
            "derived_observations": derived_observations
        }, indent=4)


def generate_prompt(data):
    """Generate a formatted prompt from the fetched data."""
    return PROMPT_TEMPLATE.format(**data)
