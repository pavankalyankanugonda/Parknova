from datetime import datetime
from models import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    slot_id = db.Column(db.String(50), db.ForeignKey('parking_slots.id'), nullable=False)
    vehicle_number = db.Column(db.String(50), nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False)  # 'Car', 'Bike', 'Electric', 'VIP'
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)  # 'Active', 'Completed', 'Cancelled'
    base_amount = db.Column(db.Float, default=0.0, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0, nullable=False)
    total_amount = db.Column(db.Float, default=0.0, nullable=False)
    qr_code = db.Column(db.String(255), nullable=True)  # File path to QR image
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Booking {self.id} | Slot: {self.slot_id} | User: {self.user_id}>"
