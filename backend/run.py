"""
Local development server entry point for the Flask backend.

Initializes and runs the Flask application with Socket.IO support on localhost:5050.
This file is used for local development only. For production deployment, use app.py
in the project root instead, which includes automatic data backfill and startup checks.

Usage:
    python -m backend.run

Configuration:
    - Reads FLASK_ENV environment variable (defaults to 'development')
    - Runs on localhost:5050 with debug mode enabled
    - Auto-reload is disabled to prevent duplicate background tasks
"""
from backend.app import create_app
import os
from backend.app import socketio


config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

print(f"[INIT] Flask app initialized in {config_name} mode")

if __name__ == '__main__':
    socketio.run(app, host="localhost", port=5050, debug=True, use_reloader=False)
