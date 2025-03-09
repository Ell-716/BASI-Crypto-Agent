# Define the prompt template
PROMPT_TEMPLATE = """
You are an expert financial analyst specializing in cryptocurrency markets. 
Your task is to analyze historical price data, technical indicators, and market sentiment 
to provide a structured investment report.

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

**⚠ Disclaimer:** This analysis is for informational purposes only and should not be considered financial advice. 
Always conduct your own research before making investment decisions.
"""


def generate_prompt(data):
    """Generate a formatted prompt from the fetched data."""
    return PROMPT_TEMPLATE.format(**data)
