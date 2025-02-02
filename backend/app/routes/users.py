from flask import Blueprint, request, jsonify
from backend.app import db
from backend.app.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

logging.basicConfig(level=logging.INFO)
users_bp = Blueprint('users', __name__, url_prefix='/users')


# Get user details
@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "preferences": user.preferences
    }), 200


# Update user preferences
@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_preferences(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if 'preferences' not in data:
        return jsonify({"error": "Missing 'preferences' in request"}), 400

    user.preferences = data['preferences']
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "Preferences updated"}), 200


# Delete user
@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
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
