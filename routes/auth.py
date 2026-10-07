from flask import Flask, render_template, request, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from models import *

auth_Bp = Blueprint('auth', __name__)

@auth_Bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    return render_template('login.html')

@auth_Bp.route('/adminlogin', methods = ['GET', 'POST'], endpoint='adminlogin')
def adminlogin():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('password')
        admin = User.query.filter_by(email=email).first()
        if not admin:
            return render_template('admin_login.html', error="Wrong Admin credentials!")
        if pwd != admin.password:
            return render_template('admin_login.html', error="Incorrect Password!")
        login_user(admin)
        return redirect(url_for('admin.admindashboard'))
    return render_template('admin_login.html')

@auth_Bp.route('/userregister', methods=['GET','POST'], endpoint='userregister')
def userregister():
    if request.method == 'POST':
        uname = request.form.get('username')
        email = request.form.get('email')
        pwd = request.form.get('password')
        role = request.form.get('role')
        user_new = User(username=uname, email=email, password=pwd, role=role)
        db.session.add(user_new)
        db.session.commit()
        if role == "staff":
            staff_new = Staff(user_id=user_new.id)
            db.session.add(staff_new)
            db.session.commit()
            return redirect(url_for('auth.stafflogin'))
        elif role == "trekker":
            trekker_new = Trekker(user_id=user_new.id)
            db.session.add(trekker_new)
            db.session.commit()
            return redirect(url_for('auth.userlogin'))
    return render_template('register.html')

@auth_Bp.route('/stafflogin', methods=['GET','POST'], endpoint='stafflogin')
def stafflogin():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('password')
        staff = User.query.filter_by(email=email, role=Role.staff).first()
        if not staff:
            return render_template('staff_login.html', error="Staff not found!")
        if staff.password != pwd:
            return render_template('staff_login.html', error="Incorrect Password!")
        if staff.staff.status == UserStatus.blacklisted:
            return "You have been blacklisted by the admin. Dashboard access denied.", 403
        if staff.staff.status == UserStatus.pending:
            return "You have not been approved by the admin yet. Dashboard access denied.", 403
        if staff.staff.status == UserStatus.rejected:
            return "The admin has rejected your request! Dashboard access denied." , 403
        login_user(staff)
        return redirect(url_for('staff.staffdashboard'))
    return render_template('staff_login.html')

@auth_Bp.route('/userlogin', methods=['GET','POST'], endpoint='userlogin')
def userlogin():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('password')
        trekker = User.query.filter_by(email=email, role=Role.trekker).first()
        if not trekker:
            return render_template('user_login.html', error="User not found!")
        if pwd != trekker.password:
            return render_template('user_login.html', error="Incorrect Password!")
        login_user(trekker)
        return redirect(url_for('user.userdashboard'))
    return render_template('user_login.html')

@auth_Bp.route('/logout', methods=['GET', 'POST'], endpoint='logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
