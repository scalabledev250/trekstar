from flask import Flask, render_template, redirect, url_for, request
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from routes.auth import auth_Bp
from routes.admin import admin_Bp
from routes.staff import staff_Bp
from routes.user import user_Bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trek.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   
app.config['SECRET_KEY'] = 'my_key'  
db.init_app(app)  

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registering Blueprints for routes
app.register_blueprint(auth_Bp)
app.register_blueprint(admin_Bp)
app.register_blueprint(staff_Bp)
app.register_blueprint(user_Bp)

with app.app_context():
    db.create_all() # Create all tables in the configured database
    admin_name = "admin"
    admin_pwd = "adm123"
    admin_email = "admin@gmail.com"
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        adm = User(username=admin_name, email=admin_email, password=admin_pwd, role=Role.admin)
        db.session.add(adm)
        db.session.commit()

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)