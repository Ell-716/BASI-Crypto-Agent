# Concise Report Template
CONCISE_PROMPT_TEMPLATE = """
Role: Cryptocurrency Market Analyst
You are a professional cryptocurrency analyst and trader with expertise in financial markets.
Provide a structured cryptocurrency market report based on the given data.
Only explain what’s observed in the data. Don’t speculate about corrections or hallucinate missing values.
Do not introduce yourself. Begin the response directly with the report content. Be concise.

### **{coin}/USDT**  
- **Current Price:** ${latest_data[close]:,.2f}  
- **Market Sentiment:** {derived_observations[trend]}  

### **📌 Recommendation**
{investment_recommendation}  

### **📊 Key Highlights**
- **Trend:** {derived_observations[trend]}  
- **Support Levels:** {derived_observations[support_levels]}  
- **Resistance Levels:** {derived_observations[resistance_levels]}  
- **Volatility:** {derived_observations[volatility]}

**⚠️ Disclaimer:** This analysis is for informational purposes only and should not be considered financial advice.  
Always conduct your own research before making investment decisions.
"""

# Define the structured prompt template
FULL_PROMPT_TEMPLATE = """
Role: Cryptocurrency Market Analyst
You are a professional cryptocurrency analyst and trader with expertise in financial markets.
Your task is to analyze the given market data, technical indicators, and trends.
Only explain what’s observed in the data. Don’t speculate about corrections or hallucinate missing values.
Provide an in-depth, structured analysis, ensuring step-by-step insights into market conditions.
Do not introduce yourself. Begin the response directly with the report content.

### **{coin}/USDT** 
- **Current Price:** ${latest_data[close]:,.2f}  
- **Market Sentiment:** {derived_observations[trend]}

### **📌 Recommendation**
{investment_recommendation}
Give explanation.


### **📈 Trend & Moving Averages**
- **50-Day SMA:** ${trend_indicators[SMA_50]:,.2f}
- **200-Day SMA:** ${trend_indicators[SMA_200]:,.2f}
- **50-Day EMA:** ${trend_indicators[EMA_50]:,.2f}
- **200-Day EMA:** ${trend_indicators[EMA_200]:,.2f}

If the price is above both the **50-SMA** and **200-SMA**, it indicates a **strong bullish trend**.
Conversely, if it is below, it signals **bearish momentum**.


### **🛑 Support & Resistance Levels**
- **Support Levels:** {derived_observations[support_levels]}
- **Resistance Levels:** {derived_observations[resistance_levels]}

If the price approaches **support**, it may **bounce back up**. If it nears **resistance**, it could **face rejection**.


### **📊 Momentum Indicators**
- **MACD Line:** {momentum_indicators[MACD]:,.2f}
- **MACD Signal Line:** {momentum_indicators[MACD_signal]:,.2f}
- **RSI (Relative Strength Index):** {momentum_indicators[RSI]:,.2f}
- **Stoch RSI (K/D):** {momentum_indicators[Stoch_RSI_K]:,.2f} / {momentum_indicators[Stoch_RSI_D]:,.2f}

If RSI is **above 70**, the market is **overbought**, and a **pullback is likely**.
If **below 30**, the market is **oversold**, indicating a potential **upward reversal**.


### **🌐 Volatility & Market Condition**
- **Bollinger Bands Upper:** ${volatility[BB_upper]:,.2f}
- **Bollinger Bands Middle:** ${volatility[BB_middle]:,.2f}
- **Bollinger Bands Lower:** ${volatility[BB_lower]:,.2f}
- **Volatility:** {derived_observations[volatility]}

A **tight Bollinger Band range** suggests **low volatility**, while a **widening range** 
indicates **increased price movement**.


**⚠️ Disclaimer:** This analysis is for informational purposes only and should not be considered financial advice.
Always conduct your own research before making investment decisions.
"""


def generate_prompt(data, report_type="concise"):
    """Generate an investment report based on the selected format."""
    if report_type == "full":
        return FULL_PROMPT_TEMPLATE.format(**data)
    return CONCISE_PROMPT_TEMPLATE.format(**data)  # Default to concise
