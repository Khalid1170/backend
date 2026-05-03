from flask import Blueprint, jsonify, request
from app.utils.auth import token_required
from app.extensions import db
import os

user_bp = Blueprint("user", __name__)


@user_bp.route("/me", methods=["GET"])
@token_required
def get_me(current_user):
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone_number": current_user.phone_number,
        "city": current_user.city,
        "profile_pic": current_user.profile_pic
    }), 200


@user_bp.route("/update", methods=["PUT"])
@token_required
def update_profile(current_user):

    data = request.form

    current_user.first_name = data.get("first_name", current_user.first_name)
    current_user.last_name = data.get("last_name", current_user.last_name)
    current_user.phone_number = data.get("phone_number", current_user.phone_number)
    current_user.city = data.get("city", current_user.city)

    # PROFILE PIC UPDATE
    file = request.files.get("profile_pic")

    if file:
        folder = os.path.join(os.getcwd(), "static/profiles")
        os.makedirs(folder, exist_ok=True)

        filename = f"{current_user.id}.png"
        file.save(os.path.join(folder, filename))

        current_user.profile_pic = filename

    db.session.commit()

    return jsonify({"message": "Profile updated"}), 200