from backend.app import create_app
import os
from backend.app import socketio


config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

print(f"[INIT] Flask app initialized in {config_name} mode")

if __name__ == '__main__':
    socketio.run(app, host="localhost", port=5050, debug=True, use_reloader=False)

