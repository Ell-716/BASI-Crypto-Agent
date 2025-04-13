from backend.app.utils.api import fetch_coin_data


def start_coin_stream(socketio_instance, app):
    def emit_coins():
        with app.app_context():
            while True:
                coins, error = fetch_coin_data()
                if not error:
                    socketio_instance.emit("coin_data", coins, namespace="/")
                socketio_instance.sleep(60)

    socketio_instance.start_background_task(emit_coins)
