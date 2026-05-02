from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Listing, ListingImage
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

    # 🔥 MULTIPLE IMAGES
    files = request.files.getlist("images")

    upload_folder = os.path.join(os.getcwd(), "static/uploads")
    os.makedirs(upload_folder, exist_ok=True)

    for i, file in enumerate(files):
        if file:
            filename = f"{listing.id}_{i}.png"
            file.save(os.path.join(upload_folder, filename))

            img = ListingImage(
                listing_id=listing.id,
                filename=filename
            )
            db.session.add(img)

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

    # 🔥 REPLACE IMAGES
    files = request.files.getlist("images")

    if files:
        # delete old images
        for img in listing.images:
            path = os.path.join(os.getcwd(), "static/uploads", img.filename)
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(img)

        # save new
        upload_folder = os.path.join(os.getcwd(), "static/uploads")
        os.makedirs(upload_folder, exist_ok=True)

        for i, file in enumerate(files):
            if file:
                filename = f"{listing.id}_{i}.png"
                file.save(os.path.join(upload_folder, filename))

                new_img = ListingImage(
                    listing_id=listing.id,
                    filename=filename
                )
                db.session.add(new_img)

    db.session.commit()

    return jsonify({"message": "Updated"}), 200


# =========================
# GET MY LISTINGS
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
            "images": [img.filename for img in l.images],
            "user_id": l.user_id,
        }
        for l in listings
    ])


# =========================
# DELETE
# =========================
@listing_bp.route("/<int:listing_id>", methods=["DELETE"])
@token_required
def delete_listing(current_user, listing_id):

    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Not found"}), 404

    if listing.user_id != current_user.id:
        return jsonify({"error": "Not allowed"}), 403

    for img in listing.images:
        path = os.path.join(os.getcwd(), "static/uploads", img.filename)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(listing)
    db.session.commit()

    return jsonify({"message": "Deleted"})


# =========================
# PUBLIC
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

        "contact_phone": listing.contact_phone,
        "contact_email": listing.contact_email,
        "contact_whatsapp": listing.contact_whatsapp,

        "images": [img.filename for img in listing.images],
        "qr_code": listing.qr_code,
    })

# =========================
# GET ALL PUBLIC LISTINGS (MARKETPLACE)
# =========================
@listing_bp.route("/all", methods=["GET"])
def get_all_listings():
    # Fetch all listings, ordered by newest first
    listings = Listing.query.order_by(Listing.id.desc()).all()

    return jsonify([
        {
            "id": l.id,
            "user_id": l.user_id,
            "make": l.make,
            "model": l.model,
            "price": l.price,
            "mileage": l.mileage,
            "fuel_type": l.fuel_type,
            "gearbox": l.gearbox,
            "images": [img.filename for img in l.images],
            # If you have a relationship set up with the User model, 
            # you can pass the city here like this:
            # "city": l.user.city if hasattr(l, 'user') and l.user else None
        }
        for l in listings
    ])