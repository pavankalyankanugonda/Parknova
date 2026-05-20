import math
from datetime import datetime

# Parking charges per hour (in INR/₹)
RATES = {
    'Car': 50,
    'Bike': 20,
    'Electric': 30,
    'VIP': 100
}

TAX_RATE = 0.18  # 18% GST

def calculate_fee(vehicle_type, entry_time, exit_time):
    """
    Calculates duration and total amount (including tax) for a booking.
    """
    if not isinstance(entry_time, datetime) or not isinstance(exit_time, datetime):
        raise ValueError("Entry and exit times must be datetime objects.")
        
    if exit_time <= entry_time:
        raise ValueError("Exit time must be after entry time.")
        
    # Calculate duration in seconds and convert to hours
    duration_seconds = (exit_time - entry_time).total_seconds()
    duration_hours = duration_seconds / 3600.0
    
    # Standard parking calculation: Round up to the nearest hour, minimum of 1 hour
    billed_hours = math.ceil(duration_hours)
    billed_hours = max(billed_hours, 1)
    
    # Get hourly rate
    hourly_rate = RATES.get(vehicle_type, 50)  # Default to Car rate if type not found
    
    # Calculate amounts
    base_amount = float(billed_hours * hourly_rate)
    tax_amount = round(base_amount * TAX_RATE, 2)
    total_amount = round(base_amount + tax_amount, 2)
    
    return {
        'duration_hours': billed_hours,
        'hourly_rate': hourly_rate,
        'base_amount': base_amount,
        'tax_amount': tax_amount,
        'total_amount': total_amount
    }
