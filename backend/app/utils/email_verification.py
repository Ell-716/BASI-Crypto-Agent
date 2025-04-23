from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app


def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm')


def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
    except SignatureExpired:
        return None  # Token is valid but expired
    except BadSignature:
        return None  # Token is invalid
    return email


def send_verification_email(email, verify_url):
    from backend.app import mail
    from flask_mail import Message

    msg = Message(
        subject="Welcome to BASI - Verify your email",
        recipients=[email],
        body=(
            "Hi there,\n\n"
            "Thanks for signing up for BASI (Blockchain AI Smart Investor)!\n\n"
            "Please confirm your email address by clicking the link below:\n\n"
            f"{verify_url}\n\n"
            "If you didn’t request this, just ignore this message.\n\n"
            "Best,\n"
            "The BASI Team"
        )
    )
    mail.send(msg)


def send_password_reset_email(email, reset_url):
    from backend.app import mail
    from flask_mail import Message

    msg = Message(
        subject="Reset your BASI password",
        recipients=[email],
        body=(
            "Hi,\n\n"
            "We received a request to reset your BASI account password.\n\n"
            f"Click the link below to reset your password:\n\n{reset_url}\n\n"
            "If you didn't request this, you can safely ignore this email.\n\n"
            "Best,\nThe BASI Team"
        )
    )
    mail.send(msg)
