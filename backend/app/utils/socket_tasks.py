from flask_socketio import emit
from backend.app.utils.api import fetch_coin_data, get_cached_coingecko_data
from backend.app.models import Coin

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
    coins, error = fetch_coin_data()
    if error or not coins:
        print(f"[SOCKET] ⚠️ Fetch error: {error}")
        return []

    # Map local coin symbols to their DB ID
    coin_ids = {c.coin_symbol.upper(): c.id for c in Coin.query.all()}

    gecko_data = get_cached_coingecko_data()
    gecko_map = {item["symbol"].upper(): item for item in gecko_data}

    for coin in coins:
        symbol = coin["symbol"].upper()
        coin["id"] = coin_ids.get(symbol)
        g = gecko_map.get(symbol)
        if g:
            coin["market_cap"] = g.get("market_cap")
            coin["global_volume"] = g.get("total_volume")

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
