from flask import Flask
from .config import Config
from .extensions import db, migrate
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.listing import listing_bp
from app.routes.payment import payment_bp
# from app.models import User
from flask_cors import CORS


def create_app():
    # app = Flask(__name__)
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    CORS(app, origins=["http://localhost:5173"]) 

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(listing_bp, url_prefix="/listing")
    app.register_blueprint(payment_bp, url_prefix="/payment")

    @app.route("/")
    def home():
        return "TagMyCar API running 🚀"

    # @app.route("/debug-user")
    # def debug_user():
    #     user = User.query.first()
    #     return {
    #         "email": user.email,
    #         "is_subscribed": user.is_subscribed
    #     }

    # # ✅ FIXED PROPERLY
    # @app.route("/fix-users")
    # def fix_users():
    #     users = User.query.all()
    #     for user in users:
    #         if user.is_subscribed is None:
    #             user.is_subscribed = False

    #     db.session.commit()
    #     return "Users fixed"

    return app