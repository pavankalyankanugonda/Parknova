import io
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db
from models.user import User
from models.parking_slot import ParkingSlot
from models.booking import Booking
from models.notification import Notification

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

admin_bp = Blueprint('admin', __name__)

# Middleware check for admin role
def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin():
        flash('Access denied. Administrators only.', 'danger')
        return False
    return True

@admin_bp.before_request
def restrict_to_admins():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if not current_user.is_admin():
        flash('Access denied. Administrators only.', 'danger')
        return redirect(url_for('user.dashboard'))

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    # Analytics
    total_users = User.query.filter_by(role='user').count()
    total_bookings = Booking.query.count()
    
    # Revenue (total amount of completed or active bookings)
    revenue_query = db.session.query(func.sum(Booking.total_amount)).filter(Booking.status != 'Cancelled').scalar()
    revenue = revenue_query if revenue_query else 0.0
    
    available_slots = ParkingSlot.query.filter_by(status='Available').count()
    occupied_slots = ParkingSlot.query.filter_by(status='Occupied').count()
    total_slots = ParkingSlot.query.count()
    
    # Recent Bookings
    bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    # All slots and users for management tabs
    all_slots = ParkingSlot.query.all()
    all_slots = sorted(all_slots, key=lambda s: (s.floor, s.id))
    all_users = User.query.filter_by(role='user').all()
    all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_bookings=total_bookings,
        revenue=revenue,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
        total_slots=total_slots,
        bookings=bookings,
        all_slots=all_slots,
        all_users=all_users,
        all_bookings=all_bookings
    )

# --- Slot Management API/Routes ---

@admin_bp.route('/admin/slots/create', methods=['POST'])
@login_required
def create_slot():
    slot_id = request.form.get('slot_id').upper().strip()
    floor = request.form.get('floor', type=int)
    slot_type = request.form.get('type')
    status = request.form.get('status', 'Available')
    
    if not slot_id or floor is None or not slot_type:
        flash('Please provide all details for the slot.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    # Check if slot exists
    existing_slot = ParkingSlot.query.get(slot_id)
    if existing_slot:
        flash('Slot ID already exists.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    new_slot = ParkingSlot(id=slot_id, floor=floor, type=slot_type, status=status)
    db.session.add(new_slot)
    db.session.commit()
    
    # Emit real-time update
    try:
        from app import socketio
        socketio.emit('slot_updated', {
            'slot_id': slot_id,
            'status': status,
            'type': slot_type,
            'floor': floor
        })
    except Exception:
        pass
        
    flash(f'Slot {slot_id} created successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/slots/update-status/<string:slot_id>', methods=['POST'])
@login_required
def update_slot_status(slot_id):
    status = request.form.get('status')
    slot = ParkingSlot.query.get(slot_id)
    
    if not slot or not status:
        return jsonify({'status': 'error', 'message': 'Slot or status not found'}), 404
        
    slot.status = status
    db.session.commit()
    
    # Emit real-time update
    try:
        from app import socketio
        socketio.emit('slot_updated', {
            'slot_id': slot_id,
            'status': status,
            'type': slot.type,
            'floor': slot.floor
        })
    except Exception:
        pass
        
    return jsonify({'status': 'success', 'message': f'Slot {slot_id} status updated to {status}'})

@admin_bp.route('/admin/slots/delete/<string:slot_id>', methods=['POST'])
@login_required
def delete_slot(slot_id):
    slot = ParkingSlot.query.get(slot_id)
    if not slot:
        flash('Slot not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    # Remove slot's bookings first or prevent deletion if active
    active_booking = Booking.query.filter_by(slot_id=slot_id, status='Active').first()
    if active_booking:
        flash('Cannot delete slot. It has an active booking.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    # Delete associated bookings
    Booking.query.filter_by(slot_id=slot_id).delete()
    db.session.delete(slot)
    db.session.commit()
    
    # Emit real-time delete
    try:
        from app import socketio
        socketio.emit('slot_deleted', {'slot_id': slot_id})
    except Exception:
        pass
        
    flash(f'Slot {slot_id} deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

# --- User Management ---

@admin_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    if user.role == 'admin':
        flash('Cannot delete an administrator account.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    # Cascade deletions are handled by relationship cascade="all, delete-orphan"
    db.session.delete(user)
    db.session.commit()
    
    flash('User and their bookings/vehicles deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

# --- Analytics Data Endpoint ---

@admin_bp.route('/admin/analytics-data')
@login_required
def analytics_data():
    # 1. Daily Booking Trends (last 7 days)
    today = datetime.utcnow().date()
    daily_trends = {}
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        daily_trends[day_str] = 0
        
    # Fetch from db
    bookings_by_day = db.session.query(
        func.date(Booking.created_at).label('date'),
        func.count(Booking.id).label('count')
    ).group_by(func.date(Booking.created_at)).filter(Booking.created_at >= (datetime.utcnow() - timedelta(days=7))).all()
    
    for row in bookings_by_day:
        date_str = row.date.strftime('%Y-%m-%d') if isinstance(row.date, datetime) or hasattr(row.date, 'strftime') else str(row.date)
        if date_str in daily_trends:
            daily_trends[date_str] = row.count
            
    # 2. Monthly Revenue (current year)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_revenue = {m: 0.0 for m in months}
    
    revenue_by_month = db.session.query(
        func.month(Booking.created_at).label('month'),
        func.sum(Booking.total_amount).label('revenue')
    ).filter(
        Booking.status != 'Cancelled',
        func.year(Booking.created_at) == today.year
    ).group_by(func.month(Booking.created_at)).all()
    
    for row in revenue_by_month:
        month_idx = int(row.month) - 1
        if 0 <= month_idx < 12:
            monthly_revenue[months[month_idx]] = float(row.revenue)

    # 3. Slot usage statistics by type
    usage_by_type = db.session.query(
        ParkingSlot.type,
        func.count(Booking.id)
    ).join(Booking, Booking.slot_id == ParkingSlot.id).group_by(ParkingSlot.type).all()
    
    slot_usage = {t: 0 for t in ['Car', 'Bike', 'Electric', 'VIP']}
    for row in usage_by_type:
        if row[0] in slot_usage:
            slot_usage[row[0]] = row[1]
            
    return jsonify({
        'daily_trends': {
            'labels': list(daily_trends.keys()),
            'data': list(daily_trends.values())
        },
        'monthly_revenue': {
            'labels': list(monthly_revenue.keys()),
            'data': list(monthly_revenue.values())
        },
        'slot_usage': {
            'labels': list(slot_usage.keys()),
            'data': list(slot_usage.values())
        }
    })

# --- PDF Report Exporter ---

@admin_bp.route('/admin/report/pdf')
@login_required
def export_pdf_report():
    # Fetch all bookings
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    
    # Create memory buffer
    buffer = io.BytesIO()
    
    # Setup ReportLab document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=15,
        alignment=1  # Centered
    )
    
    subtitle_style = ParagraphStyle(
        name='SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=20,
        alignment=1  # Centered
    )
    
    table_header_style = ParagraphStyle(
        name='TableHeaderStyle',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        name='TableCellStyle',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#334155')
    )

    story = []
    
    # Header Title
    story.append(Paragraph("ParkNova Parking System Reports", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Table columns: ID, User, Slot, Vehicle, Entry, Exit, Fee, Status
    table_data = [
        [
            Paragraph("ID", table_header_style),
            Paragraph("User Email", table_header_style),
            Paragraph("Slot ID", table_header_style),
            Paragraph("Vehicle No.", table_header_style),
            Paragraph("Entry Time", table_header_style),
            Paragraph("Exit Time", table_header_style),
            Paragraph("Fee (₹)", table_header_style),
            Paragraph("Status", table_header_style)
        ]
    ]
    
    for b in bookings:
        # Fetch user
        user = User.query.get(b.user_id)
        user_email = user.email if user else "Deleted User"
        
        table_data.append([
            Paragraph(str(b.id), table_cell_style),
            Paragraph(user_email, table_cell_style),
            Paragraph(b.slot_id, table_cell_style),
            Paragraph(b.vehicle_number, table_cell_style),
            Paragraph(b.entry_time.strftime('%Y-%m-%d %H:%M'), table_cell_style),
            Paragraph(b.exit_time.strftime('%Y-%m-%d %H:%M'), table_cell_style),
            Paragraph(f"₹{b.total_amount:.2f}", table_cell_style),
            Paragraph(b.status, table_cell_style)
        ])
        
    # Build Table
    # Width dimensions: Total 552 points available (8.5 * 72 - 60)
    col_widths = [25, 110, 50, 70, 95, 95, 52, 55]
    report_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Table Styling
    ts = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),  # Header background indigo-600
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),  # Alternate light slate and white
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    report_table.setStyle(ts)
    
    story.append(report_table)
    
    # Build document
    doc.build(story)
    
    # Set pointer to beginning of buffer
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"parknova_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf'
    )
