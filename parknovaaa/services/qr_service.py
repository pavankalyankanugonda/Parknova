import os
import qrcode
from flask import current_app

def generate_booking_qr(booking_id, vehicle_number, slot_id, entry_time, exit_time):
    """
    Generates a QR code for a booking and saves it to the static/uploads/qrcodes folder.
    Returns the relative path to the QR image.
    """
    # Create the QR content string (or JSON)
    qr_data = (
        f"ParkNova Parking Pass\n"
        f"Booking ID: {booking_id}\n"
        f"Vehicle: {vehicle_number}\n"
        f"Slot: {slot_id}\n"
        f"Entry: {entry_time.strftime('%Y-%m-%d %H:%M')}\n"
        f"Exit: {exit_time.strftime('%Y-%m-%d %H:%M')}"
    )
    
    # Configure QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Define filename and path
    filename = f"booking_{booking_id}.png"
    filepath = os.path.join(current_app.config['QR_FOLDER'], filename)
    
    # Save the image
    img.save(filepath)
    
    # Return the relative path to be stored in the database
    return f"uploads/qrcodes/{filename}"
