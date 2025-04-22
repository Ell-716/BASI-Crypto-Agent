from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app
from flask_mail import Message
from backend.app import mail


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
    msg = Message(
        subject="Verify your email",
        recipients=[email],
        body=f"Click to verify your email: {verify_url}"
    )
    mail.send(msg)
