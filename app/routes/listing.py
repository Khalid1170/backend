from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Listing
from app.utils.auth import token_required
import qrcode
import os

listing_bp = Blueprint("listing", __name__)


# =========================
# CREATE LISTING
# =========================
@listing_bp.route("/create", methods=["POST"])
@token_required
def create_listing(current_user):

    if not current_user.is_subscribed:
        return jsonify({"error": "Subscription required"}), 403

    listing = Listing(
        user_id=current_user.id,
        make=request.form.get("make"),
        model=request.form.get("model"),
        mileage=request.form.get("mileage"),
        price=request.form.get("price"),
        fuel_type=request.form.get("fuel_type"),
        gearbox=request.form.get("gearbox"),
        engine_size=request.form.get("engine_size"),
        doors=request.form.get("doors"),
        description=request.form.get("description"),
        contact_phone=request.form.get("contact_phone"),
        contact_email=request.form.get("contact_email"),
        contact_whatsapp=request.form.get("contact_whatsapp"),
    )

    db.session.add(listing)
    db.session.commit()

    # IMAGE
    file = request.files.get("image")

    if file:
        folder = os.path.join(os.getcwd(), "static/uploads")
        os.makedirs(folder, exist_ok=True)

        filename = f"{listing.id}.png"
        file.save(os.path.join(folder, filename))
        listing.image = filename

    # QR CODE
    qr_folder = os.path.join(os.getcwd(), "static/qrcodes")
    os.makedirs(qr_folder, exist_ok=True)

    qr = qrcode.make(f"http://localhost:5173/listing/{listing.id}")

    qr_filename = f"{listing.id}.png"
    qr.save(os.path.join(qr_folder, qr_filename))
    listing.qr_code = qr_filename

    db.session.commit()

    return jsonify({
        "message": "Listing created",
        "listing_id": listing.id
    }), 201


# =========================
# UPDATE LISTING
# =========================
@listing_bp.route("/update/<int:listing_id>", methods=["POST"])
@token_required
def update_listing(current_user, listing_id):

    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Not found"}), 404

    if listing.user_id != current_user.id:
        return jsonify({"error": "Not allowed"}), 403

    listing.make = request.form.get("make")
    listing.model = request.form.get("model")
    listing.mileage = request.form.get("mileage")
    listing.price = request.form.get("price")

    listing.fuel_type = request.form.get("fuel_type")
    listing.gearbox = request.form.get("gearbox")
    listing.engine_size = request.form.get("engine_size")
    listing.doors = request.form.get("doors")
    listing.description = request.form.get("description")

    listing.contact_phone = request.form.get("contact_phone")
    listing.contact_email = request.form.get("contact_email")
    listing.contact_whatsapp = request.form.get("contact_whatsapp")

    # IMAGE UPDATE
    file = request.files.get("image")

    if file:
        folder = os.path.join(os.getcwd(), "static/uploads")
        os.makedirs(folder, exist_ok=True)

        filename = f"{listing.id}.png"
        file.save(os.path.join(folder, filename))
        listing.image = filename

    db.session.commit()

    return jsonify({"message": "Updated"}), 200


# =========================
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
            "image": l.image,
            "qr_code": l.qr_code,
            "user_id": l.user_id,  # ✅ FIXED

            # SAFE SELLER INFO
            # "seller_first_name": getattr(l.user, "first_name", ""),
            # "seller_last_name": getattr(l.user, "last_name", ""),
        }
        for l in listings
    ])
# =========================
# DELETE LISTING
# =========================
@listing_bp.route("/<int:listing_id>", methods=["DELETE"])
@token_required
def delete_listing(current_user, listing_id):

    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    # 🔒 SECURITY CHECK (VERY IMPORTANT)
    if listing.user_id != current_user.id:
        return jsonify({"error": "Not allowed"}), 403

    try:
        # OPTIONAL: delete image file
        if listing.image:
            image_path = os.path.join(os.getcwd(), "static/uploads", listing.image)
            if os.path.exists(image_path):
                os.remove(image_path)

        # OPTIONAL: delete QR code file
        if listing.qr_code:
            qr_path = os.path.join(os.getcwd(), "static/qrcodes", listing.qr_code)
            if os.path.exists(qr_path):
                os.remove(qr_path)

        db.session.delete(listing)
        db.session.commit()

        return jsonify({"message": "Listing deleted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Delete failed", "details": str(e)}), 500


# =========================
# PUBLIC LISTING
# =========================
@listing_bp.route("/<int:listing_id>", methods=["GET"])
def get_listing(listing_id):

    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "id": listing.id,
        "user_id": listing.user_id,
        "make": listing.make,
        "model": listing.model,
        "mileage": listing.mileage,
        "price": listing.price,

        "fuel_type": listing.fuel_type,
        "gearbox": listing.gearbox,
        "engine_size": listing.engine_size,
        "doors": listing.doors,
        "description": listing.description,

        # SAFE SELLER INFO
        "seller_first_name": getattr(listing.user, "first_name", ""),
        "seller_last_name": getattr(listing.user, "last_name", ""),
        "seller_city": getattr(listing.user, "city", ""),

        "contact_phone": listing.contact_phone,
        "contact_email": listing.contact_email,
        "contact_whatsapp": listing.contact_whatsapp,

        "image": listing.image,
        "qr_code": listing.qr_code,
    })

