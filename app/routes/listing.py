from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Listing
from app.utils.auth import token_required
import qrcode
import os

listing_bp = Blueprint("listing", __name__)


@listing_bp.route("/create", methods=["POST"])
@token_required
def create_listing(current_user):

    if not current_user.is_subscribed:
        return jsonify({"error": "Subscription required"}), 403

    # BASIC INFO
    make = request.form.get("make")
    model = request.form.get("model")
    mileage = request.form.get("mileage")
    price = request.form.get("price")

    # NEW FIELDS
    fuel_type = request.form.get("fuel_type")
    gearbox = request.form.get("gearbox")
    engine_size = request.form.get("engine_size")
    doors = request.form.get("doors")
    description = request.form.get("description")

    # CONTACT
    contact_phone = request.form.get("contact_phone")
    contact_email = request.form.get("contact_email")
    contact_whatsapp = request.form.get("contact_whatsapp")

    file = request.files.get("image")

    listing = Listing(
        user_id=current_user.id,
        make=make,
        model=model,
        mileage=mileage,
        price=price,
        fuel_type=fuel_type,
        gearbox=gearbox,
        engine_size=engine_size,
        doors=doors,
        description=description,
        contact_phone=contact_phone,
        contact_email=contact_email,
        contact_whatsapp=contact_whatsapp,
    )

    db.session.add(listing)
    db.session.commit()

    # IMAGE
    if file:
        upload_folder = os.path.join(os.getcwd(), "static/uploads")
        os.makedirs(upload_folder, exist_ok=True)

        filename = f"{listing.id}.png"
        file.save(os.path.join(upload_folder, filename))
        listing.image = filename

    # QR CODE
    qr_folder = os.path.join(os.getcwd(), "static/qrcodes")
    os.makedirs(qr_folder, exist_ok=True)

    url = f"http://localhost:5173/listing/{listing.id}"
    qr_img = qrcode.make(url)

    qr_filename = f"{listing.id}.png"
    qr_img.save(os.path.join(qr_folder, qr_filename))

    listing.qr_code = qr_filename

    db.session.commit()

    return jsonify({
        "message": "Listing created",
        "listing_id": listing.id,
        "image": listing.image,
        "qr_code": listing.qr_code
    }), 201


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

            # NEW
            "fuel_type": l.fuel_type,
            "gearbox": l.gearbox,
            "engine_size": l.engine_size,
            "doors": l.doors,
            "description": l.description,
        }
        for l in listings
    ])


@listing_bp.route("/<int:listing_id>", methods=["GET"])
def get_listing(listing_id):

    listing = Listing.query.get(listing_id)

    if not listing:
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

        "image": listing.image,
        "qr_code": listing.qr_code
    })