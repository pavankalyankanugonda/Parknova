from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they are registered with SQLAlchemy
from models.user import User
from models.parking_slot import ParkingSlot
from models.booking import Booking
from models.vehicle import Vehicle
from models.notification import Notification
