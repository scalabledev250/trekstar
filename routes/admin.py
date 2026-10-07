from flask import Flask, render_template, request, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from models import *

admin_Bp = Blueprint('admin', __name__, url_prefix='')

@admin_Bp.route('/admindashboard', methods=['GET'], endpoint='admindashboard')
@login_required
def admindashboard():
    total_treks = Trek.query.count()
    total_staff = User.query.filter_by(role=Role.staff).count()
    total_trekkers = User.query.filter_by(role=Role.trekker).count()
    total_bookings = Booking.query.count()
    #Staff search
    staff_search = request.args.get('staff_search', '')
    if staff_search:
        sres = User.query.filter(User.role == Role.staff, User.username.ilike(f'%{staff_search}%')).all()
    else:
        sres = []  
    user_search = request.args.get('user_search', '')
    if user_search:
        res = User.query.filter(User.role == Role.user, User.username.ilike(f'%{user_search}%')).all()
    else:
        ures = []    
    trek_search = request.args.get('trek_search', '')
    if trek_search:
        tres = Trek.query.filter(Trek.name.ilike(f'%{trek_search}%')).all()
    else:
        tres = []
    return render_template('admin_dashboard.html', name=current_user.username, total_treks=total_treks, total_staff=total_staff, total_trekkers=total_trekkers, 
                           total_bookings=total_bookings,  staff_search=staff_search, sres=sres, 
                           user_search=user_search, ures=ures, trek_search=trek_search, tres=tres)


@admin_Bp.route('/managestaff', methods=['GET'], endpoint='managestaff')
@login_required
def managestaff():
    pending_staff = Staff.query.filter_by(status=UserStatus.pending).all()
    plen = len(pending_staff)
    approved_staff = Staff.query.filter_by(status=UserStatus.approved).all()
    alen = len(approved_staff)
    blackl_staff = Staff.query.filter_by(status=UserStatus.blacklisted).all()
    blen = len(blackl_staff)
    return render_template('admin_manage_staff.html', pending_staff=pending_staff, approved_staff=approved_staff, blacklisted=blackl_staff,
                            pending_length=plen, approved_length=alen, blacklist_length=blen)  

@admin_Bp.route('/approvestaff', methods=['GET', 'POST'], endpoint='approvestaff')
def approvestaff():
    pending_staff = Staff.query.filter_by(status=UserStatus.pending).all()
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        res = request.form.get('approval')
        staff = Staff.query.get_or_404(staff_id)
        if res == 'approved':
            staff.status = UserStatus.approved
        elif res == 'rejected':
            staff.status = UserStatus.rejected
        db.session.commit()
        return redirect(url_for('admin.managestaff'))

@admin_Bp.route('/remblstaff', methods=['GET', 'POST'], endpoint='remblstaff')
def remblstaff():
    approved_staff = Staff.query.filter_by(status=UserStatus.approved).all()
    if request.method == 'POST':     
        staff_id = request.form.get('staff_id')
        res = request.form.get('action')
        staff = Staff.query.get_or_404(staff_id)
        if res == 'remove':
            staff.is_deleted = True
        elif res == 'blacklist':
            staff.status = UserStatus.blacklisted
        elif res == 'remblack':
            staff.status = UserStatus.approved
        db.session.commit()
        return redirect(url_for('admin.managestaff'))


@admin_Bp.route('/addtrek', methods=['GET','POST'], endpoint='addtrek')
@login_required
def addtrek():
    all_staff = User.query.filter_by(role=Role.staff).all()
    if request.method == 'POST':
        tname = request.form.get('trekname')
        tloc = request.form.get('location')
        duration = int(request.form.get('duration'))
        diff = Diff[request.form.get('difficulty')]
        slots = int(request.form.get('available_slots'))
        sdate = datetime.strptime(request.form["start_date"],"%Y-%m-%d").date()
        edate = datetime.strptime(request.form["end_date"],"%Y-%m-%d").date()
        staff_id = int(request.form.get('assigned_staff'))
        status = TrekStatus[request.form.get('status')]
        desc = request.form.get('description')
        img = request.form.get('image')
        if sdate > edate:
            return render_template('add_trek.html', all_staff=all_staff, error="Start date cannot be after end date.")
        new_trek = Trek(
            name=tname, location=tloc, duration=duration, available_slots=slots,
            start_date=sdate, end_date=edate, difficulty=diff, status=status,
        )
        new_trek.staff_id = staff_id
        if desc:
            new_trek.description = desc
        if img:
            new_trek.image = img
        db.session.add(new_trek)
        db.session.commit()
        return redirect(url_for('admin.admindashboard'))
    return render_template('add_trek.html', all_staff=all_staff)

@admin_Bp.route('/managetrek', methods=['GET', 'POST'], endpoint='managetrek')
@login_required
def managetrek():
    treks = Trek.query.filter_by(is_deleted=False).all()
    return render_template('admin_manage_trek.html', treks=treks)

@admin_Bp.route('/viewtrek/<int:trek_id>', methods=['GET'], endpoint='viewtrek')
@login_required
def viewtrek(trek_id):
    trek = Trek.query.filter_by(id=trek_id, is_deleted=False).first()
    return render_template('view_trek_admin.html', trek=trek)

@admin_Bp.route('/edittrek/<int:trek_id>', methods=['GET', 'POST'], endpoint='edittrek')
def edittrek(trek_id):  
    trek = Trek.query.filter_by(id=trek_id, is_deleted=False).first()
    all_staff = User.query.filter_by(role=Role.staff).all()
    if request.method == 'POST':
        trek.trek_name = request.form.get('trek_name')
        trek.location = request.form.get('location')
        trek.difficulty = Diff[request.form.get('difficulty')]
        trek.duration = int(request.form.get('duration'))
        trek.available_slots = int(request.form.get('available_slots'))
        trek.status = TrekStatus[request.form.get('status')]
        trek.staff_id = int(request.form.get('assigned_staff_id'))
        desc = request.form.get('description')
        img = request.form.get('image')
        sdate = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        edate = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        if sdate > edate:
            return render_template('add_trek.html', all_staff=all_staff, error="Start date cannot be after end date.")
        trek.start_date = sdate
        trek.end_date = edate
        if desc:
            trek.description = desc
        if img:
            trek.image = img
        db.session.commit()
        return redirect(url_for('admin.managetrek'))
    return render_template('edit_trek.html', trek=trek, all_staff=all_staff)

@admin_Bp.route('/deletetrek/<int:trek_id>', methods=['POST'])
def deletetrek(trek_id):
    trek = Trek.query.get_or_404(trek_id, is_deleted=False)
    trek.is_deleted = True
    db.session.commit()
    return redirect(url_for('admin.managetrek'))


@admin_Bp.route('/manageusers', methods=['GET', 'POST'])
def manageusers():
    trekkers = Trekker.query.filter_by(status=UserStatus.approved).all()
    blist = Trekker.query.filter_by(status=UserStatus.blacklisted).all()
    tlen = Trekker.query.filter_by(status=UserStatus.approved).count()
    blen = Trekker.query.filter_by(status=UserStatus.blacklisted).count()
    if request.method == 'POST':
        trekker_id = request.form.get('trekker_id')
        res = request.form.get('action')
        trekker = Trekker.query.get_or_404(trekker_id)
        if res == 'blacklist':
            trekker.status = UserStatus.blacklisted
        elif res == 'rembl':
            trekker.status = UserStatus.approved
        elif res == 'remove':
            trekker.is_deleted = True
        db.session.commit()
        return redirect( url_for('admin.manageusers'))
    return render_template('admin_manage_users.html', trekkers=trekkers, blist=blist, tlen=tlen, blen=blen)

@admin_Bp.route('/booking', methods=['GET','POST'])
def bookings():
    bookings = Booking.query.all()
    return render_template('admin_booking.html', bookings=bookings, booklen=len(bookings))


