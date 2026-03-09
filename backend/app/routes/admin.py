from flask import Blueprint, request, jsonify
import os
from backend.app.models import db, User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/delete-user', methods=['DELETE'])
def delete_user():
    secret = os.environ.get('ADMIN_SECRET', '')
    if request.headers.get('X-Admin-Secret') != secret:
        return jsonify({"error": "Unauthorized"}), 401

    email = request.json.get('email')
    if not email:
        return jsonify({"error": "Email required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {email} deleted"}), 200
