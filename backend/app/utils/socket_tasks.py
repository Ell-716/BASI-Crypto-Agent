import time
from threading import Thread
from backend.app import socketio
from backend.app.utils.api import fetch_coin_data


def start_coin_stream():
    def emit_coins():
        while True:
            coins, error = fetch_coin_data()
            if not error:
                socketio.emit("coin_data", coins, broadcast=True)
            time.sleep(60)

    thread = Thread(target=emit_coins)
    thread.daemon = True
    thread.start()
