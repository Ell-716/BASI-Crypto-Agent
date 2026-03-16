"""
User management routes for authentication and account operations.

Handles user registration, login, email verification, password reset,
profile management, and favorite coins functionality.
"""
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


@users_bp.route('/add_user', methods=['POST'])
@limiter.limit("5 per minute")
def add_user():
    """
    Register a new user account.

    Validates password strength and username format, creates user account,
    and sends verification email.

    Returns:
        JSON response with success/error message and HTTP status code
    """
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
    """
    Verify user email address via token link.

    Endpoint: GET /users/verify?token=<token>

    Handles email verification by confirming the token and marking the user
    as verified. Renders an HTML page with the verification result.

    Query Parameters:
        token (str): Email verification token from registration email

    Returns:
        Response: HTML page showing verification status message
    """
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
    """
    Resend email verification link to user.

    Endpoint: POST /users/resend-verification

    Generates a new verification token and sends it to the user's email.
    Returns a generic message for security (doesn't reveal if email exists).
    Rate limited to 3 requests per minute.

    Request Body:
        {
            "email": str
        }

    Returns:
        Response: JSON with message (200) or error (400, 500)
    """
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
    """
    Authenticate user and issue JWT tokens.

    Endpoint: POST /users/login

    Validates credentials, checks email verification status, and issues both
    access and refresh JWT tokens for authenticated sessions. Rate limited
    to 10 requests per minute.

    Request Body:
        {
            "email": str,
            "password": str
        }

    Returns:
        Response: JSON with access_token and refresh_token (200),
                 bad request (400), invalid credentials (401),
                 or unverified email (403)
    """
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
    """
    Refresh JWT access token using refresh token.

    Endpoint: POST /users/refresh

    Issues a new access token when the current one expires. Requires a valid
    refresh token in the Authorization header. Used to maintain user sessions
    without requiring re-login.

    Headers:
        Authorization: Bearer <refresh_token>

    Returns:
        Response: JSON with new access_token (200) or unauthorized error (401)
    """
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token), 200


# Get User Details
@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Retrieve user profile information.

    Endpoint: GET /users/<user_id>

    Returns user details including email, username, and favorite coins list.
    Users can only access their own profile (enforced via JWT identity check).

    Args:
        user_id (int): Database ID of the user

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        Response: JSON with user details (200), unauthorized (403),
                 or not found (404)
    """
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
    """
    Update user profile (username and favorite coins).

    Endpoint: PUT /users/<user_id>

    Allows users to change their username and manage their favorite coins list.
    Supports adding and removing multiple coins in a single request. Users can
    only update their own profile.

    Args:
        user_id (int): Database ID of the user

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "user_name": str (optional),
            "add_coins": [int] (optional, list of coin IDs to add),
            "remove_coins": [int] (optional, list of coin IDs to remove)
        }

    Returns:
        Response: JSON with updated profile (200), unauthorized (403),
                 not found (404), or database error (500)
    """
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
    """
    Permanently delete user account.

    Endpoint: DELETE /users/<user_id>

    Removes the user account from the database. This is a destructive operation
    that cannot be undone. Users can only delete their own account. Associated
    data like favorite coins relationships are also removed.

    Args:
        user_id (int): Database ID of the user

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        Response: JSON success message (200), unauthorized (403),
                 not found (404), or database error (500)
    """
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
    """
    Request password reset link via email.

    Endpoint: POST /users/request-password-reset

    Generates a password reset token and sends it to the user's email address.
    Returns a generic message for security (doesn't reveal if email exists).
    Rate limited to 3 requests per minute to prevent abuse.

    Request Body:
        {
            "email": str
        }

    Returns:
        Response: JSON with generic success message (200),
                 bad request (400), or email error (500)
    """
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
    """
    Reset user password using token from email.

    Endpoint: POST /users/reset-password

    Validates the reset token and updates the user's password. Enforces
    password strength requirements. This completes the password reset flow
    initiated by request-password-reset.

    Request Body:
        {
            "token": str,
            "new_password": str
        }

    Returns:
        Response: JSON success message (200), bad request for missing fields
                 or weak password (400), not found if user doesn't exist (404)
    """
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
