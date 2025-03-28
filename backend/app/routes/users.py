from flask import Blueprint, request, jsonify
from backend.app.models import db, User, Coin
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
import logging
from backend.app.utils.security import is_strong_password
from backend.app.utils.email_verification import generate_verification_token, confirm_verification_token


logging.basicConfig(level=logging.INFO)
bcrypt = Bcrypt()
users_bp = Blueprint('users', __name__, url_prefix='/users')


# Register a new user
@users_bp.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    email = data.get('email')
    user_name = data.get('user_name')
    password = data.get('password')

    if not email or not password or not user_name:
        return jsonify({"error": "Missing email, password, or user_name"}), 400

    if not is_strong_password(password):
        return jsonify({
            "error": "PASSWORD MUST CONTAIN:\n"
                     "- At least one uppercase letter\n"
                     "- At least one lowercase letter\n"
                     "- At least one number\n"
                     "- At least one special character (@, #, $, etc.)\n"
                     "- Minimum 8 characters"
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password_hash=hashed_password, user_name=user_name)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

    token = generate_verification_token(email)
    verify_url = f"http://localhost:5050/users/verify?token={token}"
    print("Email verification link:", verify_url)

    return jsonify({"message": "User registered successfully"}), 201


@users_bp.route('/verify', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Missing token"}), 400

    email = confirm_verification_token(token)
    if not email:
        return jsonify({"error": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200

    user.is_verified = True
    db.session.commit()
    return jsonify({"message": "Email verified successfully"}), 200


# Login route - issue both access and refresh tokens
@users_bp.route('/login', methods=['POST'])
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

    user = User.query.get(user_id)
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

    user = User.query.get(user_id)
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
            coin = Coin.query.get(coin_id)
            if coin and coin not in user.favorite_coins:
                user.favorite_coins.append(coin)

        for coin_id in remove_coins:
            coin = Coin.query.get(coin_id)
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

    user = User.query.get(user_id)
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
