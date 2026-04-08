"""
Email verification utilities for user account confirmation.

Handles generation and validation of email verification tokens,
and sends verification emails using Resend API.
"""
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app
import resend
import os


def generate_verification_token(email):
    """Generate secure email verification token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm')


def confirm_verification_token(token, expiration=3600):
    """
    Verify email confirmation token.

    Args:
        token: Signed verification token
        expiration: Token validity in seconds (default 1 hour)

    Returns:
        Email address if valid, None if expired/invalid
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
    except SignatureExpired:
        return None  # Token is valid but expired
    except BadSignature:
        return None  # Token is invalid
    return email


def send_verification_email(email, verify_url):
    """Send email verification link via Resend API."""
    resend.api_key = current_app.config['RESEND_API_KEY']

    resend.Emails.send({
        "from": "BASI Crypto <noreply@basiai.org>",
        "to": email,
        "subject": "Welcome to BASI - Verify your email",
        "html": (
            "<p>Hi there,</p>"
            "<p>Thanks for signing up for BASI (Blockchain AI Smart Investor)!</p>"
            f"<p>Please confirm your email address by clicking <a href='{verify_url}'>here</a>.</p>"
            "<p>If you didn't request this, just ignore this message.</p>"
            "<p>Best,<br>The BASI Team</p>"
        )
    })


def send_password_reset_email(email, reset_url):
    """Send password reset link via Resend API."""
    resend.api_key = current_app.config['RESEND_API_KEY']

    resend.Emails.send({
        "from": "BASI Crypto <noreply@basiai.org>",
        "to": email,
        "subject": "Reset your BASI password",
        "html": (
            "<p>Hi,</p>"
            "<p>We received a request to reset your BASI account password.</p>"
            f"<p>Click <a href='{reset_url}'>here</a> to reset your password.</p>"
            "<p>If you didn't request this, you can safely ignore this email.</p>"
            "<p>Best,<br>The BASI Team</p>"
        )
    })
