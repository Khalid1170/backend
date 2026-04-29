from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    listings = db.relationship("Listing", backref="user", lazy=True)
    is_subscribed = db.Column(db.Boolean, default=False)


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    mileage = db.Column(db.Integer)
    price = db.Column(db.Integer)

    # NEW FIELDS
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