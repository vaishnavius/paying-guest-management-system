from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Location(db.Model):
    location_id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    pin_code = db.Column(db.String(10))

class Owner(db.Model):
    owner_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    contact_number = db.Column(db.String(15))
    password = db.Column(db.String(255))

class PGRoom(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2))
    availability_status = db.Column(db.String(20))
    facilities = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.owner_id'))

class Tenant(db.Model):
    tenant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    contact_number = db.Column(db.String(15))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    occupation = db.Column(db.String(50))

class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('pg_room.room_id'))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.tenant_id'))
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    status = db.Column(db.String(20))

class BookingHistory(db.Model):
    booking_history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('pg_room.room_id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.tenant_id'), nullable=False)
    action_type = db.Column(db.String(20), nullable=False)  # e.g., "Created", "Updated", "Cancelled"
    action_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=True)

    # Relationships (optional, for easy access if needed)
    booking = db.relationship('Booking', backref='history', lazy=True)
    room = db.relationship('PGRoom', backref='history', lazy=True)
    tenant = db.relationship('Tenant', backref='history', lazy=True)
