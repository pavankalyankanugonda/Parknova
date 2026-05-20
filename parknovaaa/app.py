import os
# pyrefly: ignore [missing-import]
from flask import Flask, render_template
# pyrefly: ignore [missing-import]
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

from config import Config
from models import db
from models.user import User
from models.parking_slot import ParkingSlot
from models.vehicle import Vehicle

# Create application instances
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)

# Initialize Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
from routes.auth import auth_bp
from routes.user import user_bp
from routes.booking import booking_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Database Initialization and Seeding
def seed_database():
    db.create_all()
    
    # Check if admin user exists, else seed
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        admin = User(
            name="System Administrator",
            email="admin@parknova.com",
            phone="+91 9999999999",
            role="admin"
        )
        admin.set_password("admin")
        db.session.add(admin)
        
    # Check if a default user exists, else seed
    test_user = User.query.filter_by(email="user@parknova.com").first()
    if not test_user:
        user = User(
            name="Regular User",
            email="user@parknova.com",
            phone="+91 8888888888",
            role="user"
        )
        user.set_password("user")
        db.session.add(user)
        db.session.commit()
        
        # Seed a test vehicle for the default user
        vehicle = Vehicle(
            user_id=user.id,
            vehicle_number="KA-03-HA-1234",
            vehicle_type="Car"
        )
        db.session.add(vehicle)

    # Seed default parking slots if grid is empty
    if ParkingSlot.query.count() == 0:
        # Create slots: floor 0 (Ground), floor 1, floor 2
        # Slot categories: Car, Bike, Electric, VIP
        slots_to_seed = [
            # Floor 0: VIP and Cars
            ParkingSlot(id="SLOT-V1", floor=0, type="VIP", status="Available"),
            ParkingSlot(id="SLOT-V2", floor=0, type="VIP", status="Available"),
            ParkingSlot(id="SLOT-C1", floor=0, type="Car", status="Available"),
            ParkingSlot(id="SLOT-C2", floor=0, type="Car", status="Available"),
            ParkingSlot(id="SLOT-C3", floor=0, type="Car", status="Available"),
            
            # Floor 1: Cars and Electric Vehicles
            ParkingSlot(id="SLOT-C4", floor=1, type="Car", status="Available"),
            ParkingSlot(id="SLOT-C5", floor=1, type="Car", status="Available"),
            ParkingSlot(id="SLOT-E1", floor=1, type="Electric", status="Available"),
            ParkingSlot(id="SLOT-E2", floor=1, type="Electric", status="Available"),
            ParkingSlot(id="SLOT-E3", floor=1, type="Electric", status="Available"),
            
            # Floor 2: Bikes
            ParkingSlot(id="SLOT-B1", floor=2, type="Bike", status="Available"),
            ParkingSlot(id="SLOT-B2", floor=2, type="Bike", status="Available"),
            ParkingSlot(id="SLOT-B3", floor=2, type="Bike", status="Available"),
            ParkingSlot(id="SLOT-B4", floor=2, type="Bike", status="Available"),
            ParkingSlot(id="SLOT-B5", floor=2, type="Bike", status="Available"),
        ]
        
        db.session.add_all(slots_to_seed)
        
    db.session.commit()

# SocketIO connection event logger
@socketio.on('connect')
def test_connect():
    print("Client connected via SocketIO WebSocket.")

@socketio.on('disconnect')
def test_disconnect():
    print("Client disconnected.")

# Bootstrapping within App Context
with app.app_context():
    seed_database()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
