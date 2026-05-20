from models import db

class ParkingSlot(db.Model):
    __tablename__ = 'parking_slots'
    
    id = db.Column(db.String(50), primary_key=True)  # e.g., "SLOT-A-101", "SLOT-E-05"
    floor = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)   # 'Car', 'Bike', 'Electric', 'VIP'
    status = db.Column(db.String(20), default='Available', nullable=False)  # 'Available', 'Occupied', 'Reserved', 'Inactive'
    
    # Relationships
    bookings = db.relationship('Booking', backref='slot', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'floor': self.floor,
            'type': self.type,
            'status': self.status
        }

    def __repr__(self):
        return f"<ParkingSlot {self.id} | Type: {self.type} | Status: {self.status}>"
