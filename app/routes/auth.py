from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User
import bcrypt
import jwt
import datetime
import os

auth_bp = Blueprint("auth", __name__)


# =========================
# REGISTER
# =========================
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()  # ✅ FIX

    email = data.get("email")
    username = data.get("username")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    city = data.get("city")
    password = data.get("password")

    if not all([email, username, first_name, last_name, phone_number, city, password]):
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user = User(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        city=city,
        password_hash=hashed_pw.decode("utf-8")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

    # profile pic
    if file:
        folder = os.path.join(os.getcwd(), "static/profiles")
        os.makedirs(folder, exist_ok=True)

        filename = f"{user.id}.png"
        file.save(os.path.join(folder, filename))

        user.profile_pic = filename
        db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# =========================
# LOGIN
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        },
        os.getenv("SECRET_KEY"),
        algorithm="HS256",
    )

    return jsonify({"token": token}), 200