from flask_socketio import emit
from backend.app.utils.api import get_cached_binance_tickers, get_cached_coingecko_data
from backend.app.models import Coin, CoinSnapshot
from backend.app.constants import TOP_10_BINANCE_COINS
from sqlalchemy import desc

socketio_instance_ref = None


def start_coin_stream(socketio_instance, app):
    global socketio_instance_ref
    socketio_instance_ref = socketio_instance

    def emit_coins():
        with app.app_context():
            while True:
                coins = prepare_coin_data()
                if coins:
                    socketio_instance.emit("coin_data", coins, namespace="/")
                    print(f"[SOCKET] 🔄 Emitted {len(coins)} coins")
                socketio_instance.sleep(60)

    socketio_instance.start_background_task(emit_coins)


def register_socket_handlers(socketio_instance, app):
    @socketio_instance.on("connect", namespace="/")
    def handle_connect():
        print("[SOCKET] ⚡ Client connected")
        emit_coin_data(socketio_instance)

    @socketio_instance.on("request_coin_data", namespace="/")
    def handle_request_coin_data():
        print("[SOCKET] 📩 Client requested coin data")
        emit_coin_data(socketio_instance)


def emit_coin_data(socketio_instance):
    coins = prepare_coin_data()
    if coins:
        emit("coin_data", coins, namespace="/")
        print("[SOCKET] ✅ Emitted coin_data to client")


def prepare_coin_data():
    """Prepare coin data from cache/DB, never blocking on API calls"""
    coins = []

    # Get cached Binance tickers (will use cache if available, try one fetch if stale)
    all_tickers = get_cached_binance_tickers()
    ticker_map = {ticker["symbol"]: ticker for ticker in all_tickers} if all_tickers else {}

    # Get all coins from DB
    coin_objs = Coin.query.all()
    coin_ids = {c.coin_symbol.upper(): c.id for c in coin_objs}

    # Get CoinGecko data if available (optional, never blocks)
    gecko_data = get_cached_coingecko_data()
    gecko_map = {item["symbol"].upper(): item for item in gecko_data} if gecko_data else {}

    # Build response for each coin
    for coin_config in TOP_10_BINANCE_COINS:
        symbol = coin_config["symbol"]
        clean_symbol = symbol.replace("USDT", "")

        # Get ticker data from cache
        ticker_data = ticker_map.get(symbol, {})

        # Get snapshot from DB for market cap
        coin_obj = Coin.query.filter_by(coin_symbol=clean_symbol).first()
        snapshot = None
        if coin_obj:
            snapshot = (
                CoinSnapshot.query
                .filter_by(coin_id=coin_obj.id)
                .order_by(desc(CoinSnapshot.timestamp))
                .first()
            )

        # Get gecko data if available
        gecko_item = gecko_map.get(clean_symbol.upper())

        coins.append({
            "id": coin_ids.get(clean_symbol.upper()),
            "symbol": clean_symbol,
            "name": coin_config["name"],
            "image": coin_config["image"],
            "current_price": float(ticker_data.get("lastPrice", 0)) if ticker_data else 0,
            "high_24h": float(ticker_data.get("highPrice", 0)) if ticker_data else 0,
            "low_24h": float(ticker_data.get("lowPrice", 0)) if ticker_data else 0,
            "total_volume": float(ticker_data.get("volume", 0)) if ticker_data else 0,
            "market_cap": snapshot.market_cap if snapshot else (gecko_item.get("market_cap") if gecko_item else None),
            "global_volume": snapshot.global_volume if snapshot else (gecko_item.get("total_volume") if gecko_item else None)
        })

    if not coins:
        print("[SOCKET] ⚠️ No coin data available")
        return []

    print(f"[SOCKET] ✅ Prepared {len(coins)} coins from cache/DB")
    return coins

def register_emit_route(app):
    @app.route("/internal/emit-coin-data", methods=["POST"])
    def trigger_emit_coin_data():
        global socketio_instance_ref
        if socketio_instance_ref is None:
            return {"error": "SocketIO instance not initialized"}, 500

        coins = prepare_coin_data()
        if coins:
            socketio_instance_ref.emit("coin_data", coins, namespace="/")
            print("[SOCKET] ✅ Manual REST emit completed")
            return {"status": "success", "emitted": len(coins)}
        return {"error": "No coins to emit"}, 500
