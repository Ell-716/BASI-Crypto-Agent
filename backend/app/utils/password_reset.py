"""
Password reset token utilities.

Handles generation and validation of time-limited password reset tokens
for secure password recovery functionality.
"""
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app


def generate_password_reset_token(email):
    """Generates a secure, time-limited password reset token for the given email."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset')


def confirm_password_reset_token(token, expiration=3600):
    """Validates password reset token and extracts email.

    Args:
        token: The password reset token to validate.
        expiration: Token validity period in seconds (default: 3600).

    Returns:
        Email address if token is valid, None otherwise.
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return serializer.loads(token, salt='password-reset', max_age=expiration)
    except (BadSignature, SignatureExpired):
        return None
