import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.booking import Booking
from models.parking_slot import ParkingSlot
from models.notification import Notification

user_bp = Blueprint('user', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
        
    # Get user statistics
    active_bookings = Booking.query.filter_by(user_id=current_user.id, status='Active').all()
    booking_history = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    
    # System statistics
    total_slots = ParkingSlot.query.count()
    available_slots = ParkingSlot.query.filter_by(status='Available').count()
    occupied_slots = ParkingSlot.query.filter_by(status='Occupied').count()
    
    # User vehicles
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    
    # Notifications (unread first)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template(
        'dashboard.html',
        active_bookings=active_bookings,
        booking_history=booking_history[:10],  # Show last 10
        total_slots=total_slots,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
        vehicles=vehicles,
        notifications=notifications
    )

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    if request.method == 'POST':
        # Update profile info
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        if not name:
            flash('Name is required.', 'danger')
            return redirect(url_for('user.profile'))
            
        current_user.name = name
        current_user.phone = phone
        
        # Profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    current_user.profile_pic = f"uploads/profile_pics/{filename}"
                else:
                    flash('Invalid image format. Allowed formats: PNG, JPG, JPEG, GIF', 'danger')
                    return redirect(url_for('user.profile'))
                    
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
        
    return render_template('profile.html', vehicles=vehicles, notifications=notifications)

@user_bp.route('/vehicle/add', methods=['POST'])
@login_required
def add_vehicle():
    vehicle_number = request.form.get('vehicle_number')
    vehicle_type = request.form.get('vehicle_type')
    
    if not vehicle_number or not vehicle_type:
        flash('Please fill in all vehicle fields.', 'danger')
        return redirect(url_for('user.profile'))
        
    vehicle_number = vehicle_number.upper().strip()
    
    # Check if vehicle number already registered globally
    existing_vehicle = Vehicle.query.filter_by(vehicle_number=vehicle_number).first()
    if existing_vehicle:
        flash('This vehicle is already registered.', 'danger')
        return redirect(url_for('user.profile'))
        
    new_vehicle = Vehicle(
        user_id=current_user.id,
        vehicle_number=vehicle_number,
        vehicle_type=vehicle_type
    )
    
    db.session.add(new_vehicle)
    db.session.commit()
    
    flash(f'Vehicle {vehicle_number} added successfully!', 'success')
    return redirect(url_for('user.profile'))

@user_bp.route('/vehicle/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=current_user.id).first()
    if not vehicle:
        flash('Vehicle not found.', 'danger')
        return redirect(url_for('user.profile'))
        
    db.session.delete(vehicle)
    db.session.commit()
    
    flash('Vehicle removed successfully.', 'success')
    return redirect(url_for('user.profile'))

@user_bp.route('/notifications/read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Notification not found'}), 404
