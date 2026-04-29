from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Listing
from app.utils.auth import token_required
import qrcode
import os

listing_bp = Blueprint("listing", __name__)


# ➕ CREATE LISTING
@listing_bp.route("/create", methods=["POST"])
@token_required
def create_listing(current_user):

    # 🔒 Subscription check
    if not current_user.is_subscribed:
        return jsonify({"error": "Subscription required"}), 403

    # ✅ CHANGE: use form data instead of JSON
    make = request.form.get("make")
    model = request.form.get("model")
    mileage = request.form.get("mileage")
    price = request.form.get("price")
    contact_phone = request.form.get("contact_phone")
    contact_email = request.form.get("contact_email")
    contact_whatsapp = request.form.get("contact_whatsapp")

    file = request.files.get("image")

    # ✅ Create listing first
    listing = Listing(
        user_id=current_user.id,
        make=make,
        model=model,
        mileage=mileage,
        price=price,
        contact_phone=contact_phone,
        contact_email=contact_email,
        contact_whatsapp=contact_whatsapp,
    )

    db.session.add(listing)
    db.session.commit()

    # ✅ HANDLE IMAGE UPLOAD
    image_path = None

    if file:
        os.makedirs("static/uploads", exist_ok=True)

        image_path = f"static/uploads/{listing.id}.png"
        file.save(image_path)

        listing.image = image_path

    # 🔗 Generate QR code (POINTS TO FRONTEND)
    url = f"http://localhost:5173/listing/{listing.id}"
    img = qrcode.make(url)

    os.makedirs("static/qrcodes", exist_ok=True)
    qr_path = f"static/qrcodes/{listing.id}.png"
    img.save(qr_path)

    listing.qr_code = qr_path

    db.session.commit()

    return jsonify({
        "message": "Listing created",
        "listing_id": listing.id,
        "qr_code": qr_path,
        "image": image_path
    }), 201


# 📄 GET MY LISTINGS
@listing_bp.route("/my", methods=["GET"])
@token_required
def get_my_listings(current_user):

    listings = Listing.query.filter_by(user_id=current_user.id).all()

    return jsonify([
        {
            "id": l.id,
            "make": l.make,
            "model": l.model,
            "price": l.price,
            "mileage": l.mileage,
            "image": l.image,      # ✅ added
            "qr_code": l.qr_code
        }
        for l in listings
    ])


# 🌍 PUBLIC LISTING (NO AUTH REQUIRED)
@listing_bp.route("/<int:listing_id>", methods=["GET"])
def get_listing(listing_id):

    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    return jsonify({
        "id": listing.id,
        "make": listing.make,
        "model": listing.model,
        "mileage": listing.mileage,
        "price": listing.price,
        "contact_phone": listing.contact_phone,
        "contact_email": listing.contact_email,
        "contact_whatsapp": listing.contact_whatsapp,
        "image": listing.image  # ✅ added
    })