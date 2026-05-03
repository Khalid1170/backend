from flask import Blueprint, jsonify, request
import stripe
import os
from app.utils.auth import token_required
from app.models import Listing
from app.extensions import db
import qrcode

payment_bp = Blueprint("payment", __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# =========================
# CREATE CHECKOUT
# =========================
@payment_bp.route("/create-checkout-session/<int:listing_id>", methods=["POST"])
@token_required
def create_checkout_session(current_user, listing_id):

    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Not found"}), 404

    if listing.user_id != current_user.id:
        return jsonify({"error": "Not allowed"}), 403

    data = request.get_json()

    # save delivery info
    listing.delivery_name = data.get("name")
    listing.delivery_address = data.get("address")
    listing.delivery_city = data.get("city")
    listing.delivery_postcode = data.get("postcode")

    db.session.commit()

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        metadata={"listing_id": listing.id},
        line_items=[{
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": f"{listing.make} {listing.model} Listing"
                },
                "unit_amount": 500,
            },
            "quantity": 1,
        }],
        success_url="http://localhost:5173/success",
        cancel_url="http://localhost:5173/dashboard",
    )

    return jsonify({"url": session.url})


# =========================
# WEBHOOK
# =========================
@payment_bp.route("/webhook", methods=["POST"])
def stripe_webhook():

    event = request.get_json()

    if event.get("type") == "checkout.session.completed":

        session = event["data"]["object"]
        listing_id = session.get("metadata", {}).get("listing_id")

        listing = Listing.query.get(listing_id)

        if listing:
            listing.is_active = True

            qr_folder = os.path.join(os.getcwd(), "static/qrcodes")
            os.makedirs(qr_folder, exist_ok=True)

            qr = qrcode.make(f"http://localhost:5173/listing/{listing.id}")
            qr_filename = f"{listing.id}.png"
            qr.save(os.path.join(qr_folder, qr_filename))

            listing.qr_code = qr_filename

            db.session.commit()

    return "", 200