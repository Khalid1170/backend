from flask import Flask, send_from_directory
from .config import Config
from .extensions import db, migrate
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)

    # =========================
    # CONFIG
    # =========================
    app.config.from_object(Config)

    # =========================
    # CORS
    # =========================
    CORS(app, origins=["http://localhost:5173"])

    # =========================
    # DB + MIGRATIONS
    # =========================
    db.init_app(app)
    migrate.init_app(app, db)

    # =========================
    # IMPORT BLUEPRINTS (INSIDE FUNCTION = IMPORTANT FIX)
    # =========================
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.listing import listing_bp
    from app.routes.payment import payment_bp

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(listing_bp, url_prefix="/listing")
    app.register_blueprint(payment_bp, url_prefix="/payment")

    # =========================
    # ROOT ROUTE
    # =========================
    @app.route("/")
    def home():
        return "TagMyCar API running 🚀"

    # =========================
    # STATIC FILES (UPLOADS)
    # =========================
    @app.route("/uploads/<filename>")
    def uploads(filename):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "uploads")
        path = os.path.abspath(path)
        return send_from_directory(path, filename)

    # =========================
    # STATIC FILES (QRCODES)
    # =========================
    @app.route("/qrcodes/<filename>")
    def qrcodes(filename):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "qrcodes")
        path = os.path.abspath(path)
        return send_from_directory(path, filename)

    # =========================
    # DEBUG ROUTE MAP (MUST BE AT END)
    # =========================
    print("REGISTERING ROUTES...")
    print(app.url_map)

    return app