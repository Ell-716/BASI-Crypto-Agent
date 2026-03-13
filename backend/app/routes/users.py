from flask import Blueprint, request, jsonify, render_template, current_app
from backend.app.models import db, User, Coin
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
import logging
from backend.app.utils.security import is_strong_password, is_valid_username
from backend.app.utils.email_verification import generate_verification_token, confirm_verification_token
from backend.app.utils.email_verification import send_verification_email
from backend.app.utils.password_reset import generate_password_reset_token, confirm_password_reset_token
from backend.app.utils.email_verification import send_password_reset_email
from backend.app.extensions import limiter


logging.basicConfig(level=logging.INFO)
bcrypt = Bcrypt()
users_bp = Blueprint('users', __name__, url_prefix='/users')


# Register a new user
@users_bp.route('/add_user', methods=['POST'])
@limiter.limit("5 per minute")
def add_user():
    data = request.get_json()
    email = data.get('email')
    user_name = data.get('user_name')
    password = data.get('password')

    if not email or not password or not user_name:
        return jsonify({"error": "Missing email, password, or username."}), 400

    if not is_strong_password(password):
        return jsonify({
            "error": "PASSWORD MUST CONTAIN:\n"
                     "- At least one uppercase letter\n"
                     "- At least one lowercase letter\n"
                     "- At least one number\n"
                     "- At least one special character (@, #, $, etc.)\n"
                     "- Minimum 8 characters"
        }), 400

    if not is_valid_username(user_name):
        return jsonify({"error": "Invalid username. Only letters, numbers, and underscores are allowed."}), 400

    existing_user = User.query.filter(User.user_name.ilike(user_name)).first()
    if existing_user:
        return jsonify({"error": "Username already exists."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password_hash=hashed_password, user_name=user_name)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Database error. Please try again."}), 500

    try:
        token = generate_verification_token(email)
        backend_url = current_app.config['BACKEND_URL']
        verify_url = f"{backend_url}/users/verify?token={token}"
        send_verification_email(email, verify_url)
        logging.info(f"Verification email sent to {email}")
    except Exception as mail_error:
        logging.error(f"Failed to send verification email to {email}: {str(mail_error)[:100]}")
        # User is created successfully, mail failure is non-fatal
        return jsonify({
            "message": "Registration successful! We couldn't send the verification email right now — please use the resend option."
        }), 201

    return jsonify({"message": "Registration successful! Please verify your email to activate your account."}), 201


@users_bp.route('/verify', methods=['GET'])
def verify_email():
    frontend_url = current_app.config['FRONTEND_URL']
    token = request.args.get('token')
    if not token:
        return render_template("verified.html", message="Missing token", frontend_url=frontend_url)

    email = confirm_verification_token(token)
    if not email:
        return render_template("verified.html", message="Invalid or expired token", frontend_url=frontend_url)

    user = User.query.filter_by(email=email).first()
    if not user:
        return render_template("verified.html", message="User not found", frontend_url=frontend_url)

    if user.is_verified:
        return render_template("verified.html", message="Email already verified", frontend_url=frontend_url)

    user.is_verified = True
    db.session.commit()
    return render_template("verified.html", message="Email verified successfully", frontend_url=frontend_url)


@users_bp.route('/resend-verification', methods=['POST'])
@limiter.limit("3 per minute")
def resend_verification():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Missing email"}), 400

    user = User.query.filter_by(email=email).first()

    # Always return the same message for security (don't reveal if email exists)
    if not user or user.is_verified:
        return jsonify({"message": "If that email exists and is unverified, a new link was sent."}), 200

    try:
        token = generate_verification_token(email)
        backend_url = current_app.config['BACKEND_URL']
        verify_url = f"{backend_url}/users/verify?token={token}"
        send_verification_email(email, verify_url)
        logging.info(f"Verification email resent to {email}")
    except Exception as mail_error:
        logging.error(f"Failed to resend verification email to {email}: {str(mail_error)[:100]}")
        return jsonify({"error": "Failed to send email. Please try again later."}), 500

    return jsonify({"message": "If that email exists and is unverified, a new link was sent."}), 200


# Login route - issue both access and refresh tokens
@users_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


# Token refresh route
@users_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token), 200


# Get User Details
@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "user_name": user.user_name,
        "favorite_coins": [coin.coin_symbol for coin in user.favorite_coins]
    }), 200


# Update user_name & favorite coins
@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user_name = data.get('user_name')
    add_coins = data.get('add_coins', [])
    remove_coins = data.get('remove_coins', [])

    if user_name:
        user.user_name = user_name

    try:
        for coin_id in add_coins:
            coin = db.session.get(Coin, coin_id)
            if coin and coin not in user.favorite_coins:
                user.favorite_coins.append(coin)

        for coin_id in remove_coins:
            coin = db.session.get(Coin, coin_id)
            if coin and coin in user.favorite_coins:
                user.favorite_coins.remove(coin)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

    return jsonify({
        "message": "User profile updated",
        "user_name": user.user_name,
        "favorite_coins": [coin.id for coin in user.favorite_coins]
    }), 200


# Delete User
@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "User deleted"}), 200


@users_bp.route('/request-password-reset', methods=['POST'])
@limiter.limit("3 per minute")
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Missing email"}), 400

    user = User.query.filter_by(email=email).first()
    # Always return the same message for security
    if not user:
        return jsonify({"message": "If that email exists, a reset link was sent."}), 200

    try:
        token = generate_password_reset_token(email)
        frontend_url = current_app.config['FRONTEND_URL']
        reset_url = f"{frontend_url}/reset-password?token={token}"
        send_password_reset_email(email, reset_url)
        logging.info(f"Password reset email sent to {email}")
    except Exception as mail_error:
        logging.error(f"Failed to send password reset email to {email}: {str(mail_error)[:100]}")
        return jsonify({"error": "Failed to send email. Please try again later."}), 500

    return jsonify({"message": "If that email exists, a reset link was sent."}), 200


@users_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({"error": "Missing token or new password"}), 400

    email = confirm_password_reset_token(token)
    if not email:
        return jsonify({"error": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not is_strong_password(new_password):
        return jsonify({
            "error": "PASSWORD MUST CONTAIN:\n"
                     "- At least one uppercase letter\n"
                     "- At least one lowercase letter\n"
                     "- At least one number\n"
                     "- At least one special character (@, #, $, etc.)\n"
                     "- Minimum 8 characters"
        }), 400

    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": "Password has been reset successfully"}), 200
