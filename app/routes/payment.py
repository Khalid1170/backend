from flask import Blueprint, jsonify, request
import stripe
import os
from datetime import datetime, timedelta
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

    # Save delivery info
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
                    "name": f"QR Kit & 30-Day Listing: {listing.make} {listing.model}",
                    "description": "Professional QR tag printing and 30 days of hosting."
                },
                "unit_amount": 1500,
            },
            "quantity": 1,
        }],
        success_url=f"http://localhost:5173/success/{listing.id}",
        cancel_url="http://localhost:5173/dashboard",
    )

    return jsonify({"url": session.url})


# =========================
# STRIPE WEBHOOK (FIXED)
# =========================
@payment_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    event = request.get_json()

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        listing_id = session.get("metadata", {}).get("listing_id")

        listing = Listing.query.get(listing_id)

        if listing:
            now = datetime.utcnow()

            # ✅ Activate listing
            listing.is_active = True

            # ✅ Proper 30-day logic
            if listing.expiry_date and listing.expiry_date > now:
                listing.expiry_date += timedelta(days=30)
            else:
                listing.expiry_date = now + timedelta(days=30)

            # =========================
            # ✅ GENERATE QR CODE
            # =========================
            qr_data = f"http://localhost:5173/listing/{listing.id}"

            qr = qrcode.make(qr_data)

            qr_folder = os.path.join(os.getcwd(), "static/qrcodes")
            os.makedirs(qr_folder, exist_ok=True)

            filename = f"{listing.id}.png"
            filepath = os.path.join(qr_folder, filename)

            qr.save(filepath)

            # ✅ Save filename to DB
            listing.qr_code = filename

            db.session.commit()

    return "", 200