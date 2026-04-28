from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User
import bcrypt
import jwt
import datetime
import os

auth_bp = Blueprint("auth", __name__)


# 🔐 REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    # check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # hash password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user = User(email=email, password_hash=hashed_pw.decode("utf-8"))

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# 🔓 LOGIN
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

    # generate token
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        },
        os.getenv("SECRET_KEY"),
        algorithm="HS256",
    )

    return jsonify({"token": token}), 200