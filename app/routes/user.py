from flask import Blueprint, jsonify
from app.utils.auth import token_required

user_bp = Blueprint("user", __name__)

@user_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    return jsonify({
        "id": current_user.id,
        "email": current_user.email
    })

