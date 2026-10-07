from flask import Flask, render_template, request, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from models import *

staff_Bp = Blueprint('staff', __name__)

# Bookings that count as real participants (cancelled/open ones are excluded)
ACTIVE_STATUSES = [BookStatus.booked, BookStatus.completed]

def staff_participant_query(staff):
    """Bookings made on treks assigned to this staff member."""
    return (Booking.query
            .join(Trek, Booking.trek_id == Trek.id)
            .filter(Trek.staff_id == staff.id,
                    Trek.is_deleted == False,
                    Booking.status.in_(ACTIVE_STATUSES)))

@staff_Bp.route('/staffdashboard')
@login_required
def staffdashboard():
    staff = getattr(current_user, "staff", None)   # Trek.staff_id points to Staff.id, not User.id
    assigned_treks = []
    participants = 0
    if staff:
        assigned_treks = Trek.query.filter_by(staff_id=staff.id, is_deleted=False).all()
        participants = staff_participant_query(staff).count()
    alen = len(assigned_treks)
    total_users = User.query.filter_by(role=Role.trekker).count()
    open_treks = Trek.query.filter_by(status=TrekStatus.open).count()
    return render_template('staff_dashboard.html', name=current_user.username, assigned_treks=assigned_treks, total_users=total_users,
                           open_treks=open_treks, participants=participants, alen=alen)

@staff_Bp.route('/stafftrek')
@login_required
def stafftrek():
    staff = getattr(current_user, "staff", None)
    assigned_treks = []
    if staff:
        assigned_treks = Trek.query.filter_by(staff_id=staff.id, is_deleted=False).all()
    return render_template('staff_manage_trek.html', assigned_treks=assigned_treks, name=current_user.username)

@staff_Bp.route('/participants')
@login_required
def participants():
    staff = getattr(current_user, "staff", None)
    participants = []
    if staff:
        participants = (staff_participant_query(staff)
                        .order_by(Booking.booking_date.desc())
                        .all())
    return render_template('staff_participants.html', participants=participants, plen=len(participants), name=current_user.username)

@staff_Bp.route('/edittrek/<int:trek_id>', methods=['GET', 'POST'])
@login_required
def edittrek(trek_id):

    trek = Trek.query.filter_by(
        id=trek_id,
        is_deleted=False
    ).first_or_404()

    if request.method == 'POST':

        try:
            trek.available_slots = int(
                request.form['available_slots']
            )

            trek.status = TrekStatus(
                request.form['status']
            )

        except (ValueError, TypeError):
            return "Invalid input", 400

        if trek.available_slots < 0:
            return "Slots cannot be negative", 400

        db.session.commit()

        return redirect(url_for('staff.stafftrek'))

    return render_template(
        'staff_edit_trek.html',
        trek=trek
    )
