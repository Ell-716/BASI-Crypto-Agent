# ₿A$I – Blockchain AI Smart Investor

₿A$I is an AI-powered crypto assistant that monitors the market, analyzes technical indicators, and provides intelligent, explainable trading insights. Designed for accessibility, it offers real-time updates, charts, and predictions to help users make informed decisions.

---

## 🚀 Features

- ✅ AI-powered predictions with natural language reasoning
- ✅ Real-time WebSocket dashboard with live updates
- ✅ Fear & Greed Index integration
- ✅ Top 24h trading volume and sparkline charts
- ✅ Coin detail pages with TradingView charts and coin info
- ✅ Full user authentication (JWT + Bcrypt + Flask-Mail)
- ✅ Mobile-responsive dark/light mode UI

---

## 🧠 Tech Stack

### Backend
- **Python**, **Flask**, **SQLAlchemy**
- **Cron** for background tasks
- **pandas-ta**, **Matplotlib**, **NumPy**, **Pandas**
- **Groq LLM** (llama-3.3-70b model for predictions)
- **WebSocket** via Flask-SocketIO

### Frontend
- **React**, **Tailwind CSS**, **Vite**
- **TradingView widget** for live charts

### Database
- **SQLite** (MVP) with future migration to **PostgreSQL**

### APIs
- **Binance API** – hourly OHLCV historical data
- **CoinGecko API** – coin metadata, market cap, volume
- **Alternative.me API** – Fear & Greed Index

## ⚙️ Setup Instructions

1. **Clone the repo**
```bash
git clone https://github.com/Ell-716/BASI-Crypto-Agent.git
cd BASI-Crypto-Agent
```

2. **Backend Setup**
```bash
# Create virtual environment (if not already present)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your actual API keys and credentials
```

3. **Start the Backend Server**
```bash
python app.py
```

4. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

5. **Set up Cron Jobs (Optional)**
```bash
# Example: Run every hour to update market data
0 * * * * /path/to/BASI-Crypto-Agent/.venv/bin/python /path/to/BASI-Crypto-Agent/backend/cron_update.py
```

## 📈 Future Roadmap

- [ ] Deploy the app
- [ ] Add future-style predictions & strategy layer
- [ ] Migrate from SQLite to PostgreSQL
- [ ] Switch from Flask to FastAPI

## 📝 License
This project is for educational/demo purposes. Not financial advice. 




