from backend.app.utils.api import fetch_coin_data, get_cached_coingecko_data


def start_coin_stream(socketio_instance, app):
    def emit_coins():
        with app.app_context():
            while True:
                coins, error = fetch_coin_data()
                if error:
                    print(f"[SOCKET] Error fetching coin data: {error}")
                    socketio_instance.sleep(60)
                    continue

                gecko_data = get_cached_coingecko_data()

                # Merge CoinGecko global market_cap + volume into each coin
                gecko_map = {item["symbol"].upper(): item for item in gecko_data}
                for coin in coins:
                    g = gecko_map.get(coin["symbol"].upper())
                    if g:
                        coin["market_cap"] = g.get("market_cap")
                        coin["global_volume"] = g.get("total_volume")

                # Emit updated payload
                socketio_instance.emit("coin_data", coins, namespace="/")
                print(f"[SOCKET] Emitting {len(coins)} coins")
                socketio_instance.sleep(60)

    socketio_instance.start_background_task(emit_coins)
