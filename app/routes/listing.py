from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Listing, ListingImage
from app.utils.auth import token_required
import os

listing_bp = Blueprint("listing", __name__)


# =========================
# CREATE LISTING
# =========================
@listing_bp.route("/create", methods=["POST"])
@token_required
def create_listing(current_user):
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
        location=request.form.get("location"),
        is_active=False
    )

    db.session.add(listing)
    db.session.commit()

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
    listing.location = request.form.get("location")

    listing.contact_phone = request.form.get("contact_phone")
    listing.contact_email = request.form.get("contact_email")
    listing.contact_whatsapp = request.form.get("contact_whatsapp")

    files = request.files.getlist("images")

    if files:
        # delete old images
        for img in listing.images:
            path = os.path.join(os.getcwd(), "static/uploads", img.filename)
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(img)

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
# GET MY LISTINGS (ARRAY)
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
            "is_active": l.is_active,
            "location": l.location
        }
        for l in listings
    ])


# =========================
# GET SINGLE PRIVATE LISTING (FIX FOR CHECKOUT)
# =========================
@listing_bp.route("/mine/<int:listing_id>", methods=["GET"])
@token_required
def get_my_single_listing(current_user, listing_id):
    # This allows the owner to fetch their own listing even if is_active=False
    listing = Listing.query.filter_by(id=listing_id, user_id=current_user.id).first()

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    return jsonify({
        "id": listing.id,
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
        "location": listing.location,
        "is_active": listing.is_active
    })


# =========================
# PUBLIC LISTING
# =========================
@listing_bp.route("/<int:listing_id>", methods=["GET"])
def get_listing(listing_id):
    listing = Listing.query.get(listing_id)

    if not listing or not listing.is_active:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "id": listing.id,
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
        "location": listing.location
    })


# =========================
# MARKETPLACE
# =========================
@listing_bp.route("/all", methods=["GET"])
def get_all_listings():
    listings = Listing.query.filter_by(is_active=True).order_by(Listing.id.desc()).all()

    return jsonify([
        {
            "id": l.id,
            "make": l.make,
            "model": l.model,
            "price": l.price,
            "mileage": l.mileage,
            "images": [img.filename for img in l.images],
            "location": l.location
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
        return jsonify({"error": "Not found"}), 404

    if listing.user_id != current_user.id:
        return jsonify({"error": "Not allowed"}), 403

    try:
        # delete images
        for img in listing.images:
            path = os.path.join(os.getcwd(), "static/uploads", img.filename)
            if os.path.exists(path):
                os.remove(path)

        db.session.delete(listing)
        db.session.commit()

        return jsonify({"message": "Deleted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500