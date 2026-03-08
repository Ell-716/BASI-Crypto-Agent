from flask import Blueprint, jsonify
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/backfill', methods=['POST'])
def run_backfill():
    # Simple secret check to prevent anyone else triggering this
    secret = os.environ.get('ADMIN_SECRET', '')
    from flask import request
    if request.headers.get('X-Admin-Secret') != secret:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        from backfill import backfill_historical_data, seed_descriptions
        backfill_historical_data()
        seed_descriptions()
        return jsonify({"message": "Backfill complete"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
