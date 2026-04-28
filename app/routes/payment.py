from flask import Blueprint, jsonify, request
import stripe
import os
from app.utils.auth import token_required
from app.models import User
from app.extensions import db

payment_bp = Blueprint("payment", __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# 💳 CREATE CHECKOUT SESSION
@payment_bp.route("/create-checkout-session", methods=["POST"])
@token_required
def create_checkout_session(current_user):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",

            # ✅ LINK USER TO STRIPE
            metadata={
                "user_id": current_user.id
            },

            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": "TagMyCar Subscription",
                    },
                    "unit_amount": 1000,
                    "recurring": {"interval": "month"},
                },
                "quantity": 1,
            }],

            success_url="http://localhost:5173/success",
            cancel_url="http://localhost:5173/cancel",
        )

        return jsonify({"url": session.url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔔 STRIPE WEBHOOK
@payment_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    event = request.get_json()

    print("🔔 Webhook received:", event.get("type"))

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]

        user_id = session.get("metadata", {}).get("user_id")

        if not user_id:
            print("❌ No user_id in metadata")
            return "", 400

        user = User.query.get(user_id)

        if user:
            user.is_subscribed = True
            db.session.commit()
            print(f"✅ User {user.email} subscribed")

    return "", 200