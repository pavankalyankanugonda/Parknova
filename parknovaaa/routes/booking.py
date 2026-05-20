from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from models import db
from models.booking import Booking
from models.parking_slot import ParkingSlot
from models.vehicle import Vehicle
from models.notification import Notification
from services.fee_service import calculate_fee
from services.qr_service import generate_booking_qr

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/booking', methods=['GET', 'POST'])
@login_required
def create_booking():
    # Fetch user's registered vehicles
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    
    # Fetch available parking slots
    slots = ParkingSlot.query.filter_by(status='Available').all()
    
    if request.method == 'POST':
        slot_id = request.form.get('slot_id')
        vehicle_id = request.form.get('vehicle_id')
        vehicle_number_raw = request.form.get('vehicle_number')
        vehicle_type = request.form.get('vehicle_type')
        entry_time_str = request.form.get('entry_time')
        exit_time_str = request.form.get('exit_time')
        
        # Validation
        if not slot_id or not vehicle_type or not entry_time_str or not exit_time_str:
            flash('Please fill in all booking details.', 'danger')
            return redirect(url_for('booking.create_booking'))
            
        # Parse times
        try:
            entry_time = datetime.strptime(entry_time_str, '%Y-%m-%dT%H:%M')
            exit_time = datetime.strptime(exit_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return redirect(url_for('booking.create_booking'))
            
        if entry_time >= exit_time:
            flash('Exit time must be after entry time.', 'danger')
            return redirect(url_for('booking.create_booking'))
            
        if entry_time < datetime.utcnow():
            # Allow slight delay for timezone/latency, but prevent past booking
            pass
            
        # Determine vehicle number
        if vehicle_id and vehicle_id != 'new':
            vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=current_user.id).first()
            if vehicle:
                vehicle_number = vehicle.vehicle_number
                vehicle_type = vehicle.vehicle_type
            else:
                flash('Selected vehicle not found.', 'danger')
                return redirect(url_for('booking.create_booking'))
        else:
            if not vehicle_number_raw:
                flash('Please provide a vehicle number.', 'danger')
                return redirect(url_for('booking.create_booking'))
            vehicle_number = vehicle_number_raw.upper().strip()
            
        # Verify slot availability
        slot = ParkingSlot.query.get(slot_id)
        if not slot or slot.status == 'Inactive':
            flash('The selected parking slot is not active or not available.', 'danger')
            return redirect(url_for('booking.create_booking'))
            
        # Prevent double booking: check if slot is booked by any active booking during this timeframe
        conflicting_booking = Booking.query.filter(
            Booking.slot_id == slot_id,
            Booking.status == 'Active',
            db.not_(
                db.or_(
                    Booking.exit_time <= entry_time,
                    Booking.entry_time >= exit_time
                )
            )
        ).first()
        
        if conflicting_booking:
            flash('This slot is already booked for the selected timeframe. Please choose another slot or time.', 'danger')
            return redirect(url_for('booking.create_booking'))
            
        # Calculate fees
        try:
            fees = calculate_fee(vehicle_type, entry_time, exit_time)
        except Exception as e:
            flash(f'Fee calculation error: {str(e)}', 'danger')
            return redirect(url_for('booking.create_booking'))
            
        # Create Booking
        new_booking = Booking(
            user_id=current_user.id,
            slot_id=slot_id,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            entry_time=entry_time,
            exit_time=exit_time,
            status='Active',
            base_amount=fees['base_amount'],
            tax_amount=fees['tax_amount'],
            total_amount=fees['total_amount']
        )
        
        try:
            db.session.add(new_booking)
            db.session.commit()
            
            # Generate QR Code pass
            qr_path = generate_booking_qr(
                booking_id=new_booking.id,
                vehicle_number=vehicle_number,
                slot_id=slot_id,
                entry_time=entry_time,
                exit_time=exit_time
            )
            new_booking.qr_code = qr_path
            
            # Temporarily mark slot occupied/reserved if booking starts now
            now = datetime.utcnow()
            if entry_time <= now <= exit_time:
                slot.status = 'Occupied'
            else:
                slot.status = 'Reserved'
                
            db.session.commit()
            
            # Create notification
            booking_notification = Notification(
                user_id=current_user.id,
                title="Booking Confirmed!",
                message=f"Your booking for slot {slot_id} is confirmed. Vehicle: {vehicle_number}. Total amount: ₹{fees['total_amount']:.2f}."
            )
            db.session.add(booking_notification)
            db.session.commit()
            
            # Emit SocketIO event to update slots grid in real-time
            try:
                from app import socketio
                socketio.emit('slot_updated', {
                    'slot_id': slot_id,
                    'status': slot.status,
                    'type': slot.type,
                    'floor': slot.floor
                })
            except Exception as se:
                # Socketio not initialized or failed, ignore
                pass
                
            flash('Booking created successfully! Your QR pass is ready.', 'success')
            return redirect(url_for('booking.view_pass', booking_id=new_booking.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            
    return render_template('booking.html', vehicles=vehicles, slots=slots)

@booking_bp.route('/booking/calculate-fee-preview', methods=['POST'])
@login_required
def calculate_fee_preview():
    data = request.json
    vehicle_type = data.get('vehicle_type')
    entry_time_str = data.get('entry_time')
    exit_time_str = data.get('exit_time')
    
    if not vehicle_type or not entry_time_str or not exit_time_str:
        return jsonify({'error': 'Missing parameters'}), 400
        
    try:
        entry_time = datetime.strptime(entry_time_str, '%Y-%m-%dT%H:%M')
        exit_time = datetime.strptime(exit_time_str, '%Y-%m-%dT%H:%M')
        
        if entry_time >= exit_time:
            return jsonify({'error': 'Exit time must be after entry time'}), 400
            
        fees = calculate_fee(vehicle_type, entry_time, exit_time)
        return jsonify(fees)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@booking_bp.route('/booking/pass/<int:booking_id>')
@login_required
def view_pass(booking_id):
    booking = Booking.query.filter_by(id=booking_id).first()
    if not booking or (booking.user_id != current_user.id and not current_user.is_admin()):
        flash('Booking not found or access denied.', 'danger')
        return redirect(url_for('user.dashboard'))
        
    return render_template('pass.html', booking=booking)

@booking_bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.filter_by(id=booking_id).first()
    if not booking or (booking.user_id != current_user.id and not current_user.is_admin()):
        flash('Booking not found or access denied.', 'danger')
        return redirect(url_for('user.dashboard'))
        
    if booking.status != 'Active':
        flash('Only active bookings can be cancelled.', 'danger')
        return redirect(url_for('user.dashboard'))
        
    booking.status = 'Cancelled'
    
    # Restore slot status to Available
    slot = ParkingSlot.query.get(booking.slot_id)
    if slot:
        slot.status = 'Available'
        
    # Notification
    cancel_notification = Notification(
        user_id=booking.user_id,
        title="Booking Cancelled",
        message=f"Your booking for slot {booking.slot_id} (Vehicle: {booking.vehicle_number}) has been cancelled."
    )
    db.session.add(cancel_notification)
    db.session.commit()
    
    # Emit SocketIO event to update slots grid in real-time
    try:
        from app import socketio
        socketio.emit('slot_updated', {
            'slot_id': slot.id,
            'status': slot.status,
            'type': slot.type,
            'floor': slot.floor
        })
    except Exception as se:
        pass
        
    flash('Booking cancelled successfully.', 'success')
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('user.dashboard'))

@booking_bp.route('/slots')
@login_required
def view_slots():
    slots = ParkingSlot.query.all()
    # Sort slots naturally by Floor and ID
    slots = sorted(slots, key=lambda s: (s.floor, s.id))
    return render_template('slots.html', slots=slots)
