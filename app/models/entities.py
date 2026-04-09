from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    hostel_id = db.Column(db.String(30), unique=True, nullable=False)
    branch = db.Column(db.String(80), default="General")
    year = db.Column(db.Integer, default=1)
    medical_profile = db.Column(db.Text, default="No known conditions")
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=True)

    complaints = db.relationship("Complaint", backref="student", lazy=True)
    fees = db.relationship("Fee", backref="student", lazy=True)
    outpasses = db.relationship("Outpass", backref="student", lazy=True)
    votes = db.relationship("Vote", backref="student", lazy=True)
    marketplace_items = db.relationship("MarketplaceItem", backref="seller", lazy=True)
    lost_found_items = db.relationship("LostFoundItem", backref="reporter", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    block = db.Column(db.String(20), nullable=False)
    floor = db.Column(db.Integer, default=1)
    capacity = db.Column(db.Integer, default=3)

    beds = db.relationship("Bed", backref="room", lazy=True, cascade="all, delete-orphan")
    inventory_items = db.relationship("Inventory", backref="room", lazy=True, cascade="all, delete-orphan")
    residents = db.relationship("User", backref="room", lazy=True)

    @property
    def occupied(self):
        return len(self.residents)

    @property
    def available(self):
        return max(self.capacity - self.occupied, 0)


class Bed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(30), default="Good")
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    penalty = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship("Payment", backref="fee", lazy=True, cascade="all, delete-orphan")


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fee_id = db.Column(db.Integer, db.ForeignKey("fee.id"), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20), default="UPI")
    txn_ref = db.Column(db.String(80), nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), default="Operations")
    spent_on = db.Column(db.Date, default=date.today)


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    vendor = db.Column(db.String(100), default="Unassigned")
    status = db.Column(db.String(20), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Outpass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    date_from = db.Column(db.Date, nullable=False)
    date_to = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    qr_token = db.Column(db.String(100), nullable=False)


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    item = db.Column(db.String(120), nullable=False)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rating = db.Column(db.Integer, default=3)


class MarketplaceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="Available")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LostFoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(140), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
