from flask import Flask, render_template, request, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from models import *

user_Bp = Blueprint('user', __name__)

@user_Bp.route('/userdashboard', methods=['GET', 'POST'])
@login_required
def userdashboard():
    available_treks = Trek.query.filter_by(status=TrekStatus.open).all()
    my_bookings = []
    if getattr(current_user, "trekker", None):
        my_bookings = Booking.query.filter_by(trekker_id=current_user.trekker.id).all()
    booked_trek_ids = [ b.trek_id for b in my_bookings if b.status == BookStatus.booked ]
    return render_template(
        "user_dashboard.html",
        name=current_user.username,
        available_treks=available_treks,
        alen=len(available_treks),
        my_bookings=my_bookings,
        booklen=len(my_bookings),
        booked_trek_ids=booked_trek_ids
    )

@user_Bp.route("/booktrek", methods=["POST"])
@login_required
def booktrek():
    trek_id = request.form.get("trek_id")
    trek = Trek.query.get_or_404(trek_id)
    trekker = current_user.trekker
    if trekker is None:
        trekker = Trekker(user_id=current_user.id)
        db.session.add(trekker)
        db.session.flush()
    # Prevent duplicate booking
    existing_booking = Booking.query.filter_by(
        trek_id=trek.id,
        trekker_id=trekker.id,
        status=BookStatus.booked).first()
    if existing_booking:
        return redirect(url_for("user.userdashboard"))
    # Prevent booking when no slots are available
    if trek.available_slots <= 0:
        return redirect(url_for("user.userdashboard"))

    booking = Booking(
        trek_id=trek.id,
        trekker_id=trekker.id,
        status=BookStatus.booked
    )

    trek.available_slots -= 1
    booking.participants = (booking.participants or 0) + 1

    db.session.add(booking)
    db.session.commit()

    return redirect(url_for("user.userdashboard"))

@user_Bp.route('/cancelbooking/<int:booking_id>', methods=['POST'])
@login_required
def cancelbooking(booking_id):
    trekker = current_user.trekker
    booking = Booking.query.filter_by(
        id=booking_id, trekker_id=trekker.id, status=BookStatus.booked
    ).first_or_404()
    trek = booking.treks            # use the booking's own trek, not a form value
    booking.status = BookStatus.cancelled
    booking.participants = max(0, (booking.participants or 0) - 1)
    trek.available_slots = (trek.available_slots or 0) + 1
    db.session.commit()
    return redirect(url_for('user.mybookings'))

@user_Bp.route('/mybookings', methods=['GET', 'POST'])
@login_required
def mybookings():
    bookings = []
    if getattr(current_user, "trekker", None):
        bookings = Booking.query.filter_by(
            trekker_id=current_user.trekker.id,
            status=BookStatus.booked
        ).all()
    return render_template('user_bookings.html', bookings=bookings)

@user_Bp.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    bookings = []
    if getattr(current_user, "trekker", None):
        bookings = Booking.query.filter_by(
            trekker_id=current_user.trekker.id
        ).order_by(Booking.booking_date.desc()).all()
    return render_template('user_history.html', bookings=bookings)