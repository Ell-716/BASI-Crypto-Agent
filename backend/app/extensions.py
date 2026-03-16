"""
Flask extensions module.

Initializes and configures Flask extensions used across the application.
Currently configures Flask-Limiter for rate limiting API endpoints.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Using in-memory storage for development
# For production, consider using Redis: storage_uri="redis://localhost:6379"
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://"
)
