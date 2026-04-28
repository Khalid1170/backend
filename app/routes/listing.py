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

    # 🔒 Subscription check (must be first)
    if not current_user.is_subscribed:
        return jsonify({"error": "Subscription required"}), 403

    data = request.get_json()

    listing = Listing(
        user_id=current_user.id,
        make=data.get("make"),
        model=data.get("model"),
        mileage=data.get("mileage"),
        price=data.get("price"),
        contact_phone=data.get("contact_phone"),
        contact_email=data.get("contact_email"),
        contact_whatsapp=data.get("contact_whatsapp"),
    )

    db.session.add(listing)
    db.session.commit()

    # 🔗 Generate QR code after DB commit (so listing.id exists)
    url = f"http://127.0.0.1:5000/listing/{listing.id}"
    img = qrcode.make(url)

    # Save QR image
    qr_path = f"qrcodes/{listing.id}.png"
    os.makedirs("qrcodes", exist_ok=True)
    img.save(qr_path)

    listing.qr_code = qr_path
    db.session.commit()

    return jsonify({
        "message": "Listing created",
        "listing_id": listing.id,
        "qr_code": qr_path
    }), 201


# 📄 GET MY LISTINGS
@listing_bp.route("/my", methods=["GET"])
@token_required
def get_my_listings(current_user):

    listings = Listing.query.filter_by(user_id=current_user.id).all()

    result = []
    for l in listings:
        result.append({
            "id": l.id,
            "make": l.make,
            "model": l.model,
            "price": l.price,
            "qr_code": l.qr_code
        })

    return jsonify(result)


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
        "contact_whatsapp": listing.contact_whatsapp
    })