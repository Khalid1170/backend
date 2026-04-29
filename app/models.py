from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)

    phone_number = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(80), nullable=False)

    profile_pic = db.Column(db.String(255), nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)

    is_subscribed = db.Column(db.Boolean, default=False)

    listings = db.relationship("Listing", backref="user", lazy=True)


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    mileage = db.Column(db.Integer)
    price = db.Column(db.Integer)

    fuel_type = db.Column(db.String(50))
    gearbox = db.Column(db.String(50))
    engine_size = db.Column(db.String(20))
    doors = db.Column(db.String(10))
    description = db.Column(db.Text)

    image = db.Column(db.String(255), nullable=True)
    qr_code = db.Column(db.String(255), nullable=True)

    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(120))
    contact_whatsapp = db.Column(db.String(50))