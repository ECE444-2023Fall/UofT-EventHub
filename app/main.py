from flask import Flask, render_template, session, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager
from forms import LoginForm, RegForm
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

## Initialize and import databases schemas
db = SQLAlchemy()
from database import Credentials

## Global constants
DB_NAME = "database.db"
R_USER = "user"
R_ORGANIZER = "organizer"

def create_app(debug):
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = '4829jfnwurduh4293k'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    bootstrap = Bootstrap(app=app)

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(username):
        return Credentials.query.get(username)

    return app

def create_database(app):
    if not path.exists(DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

app = create_app(debug = True)

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Authenticate the entry
        print(f"Entered Data: ({username}, {password})")
        user = Credentials.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)

                # Redirection to the correct home page
                if (user.role == 0):
                    return redirect(url_for('user_main'))
                else:
                    return redirect(url_for('organizer_main'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if form.validate_on_submit():
        role = form.role.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        # Authenticate the entry and add it to the database
        user = Credentials.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', category='error')
        elif len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            print(f"Entered Data: ({username}, {password1}, {role})")
            if (role == "user"):
                new_user = Credentials(username=username, password=generate_password_hash(
                password1, method='sha256'), role = 0)
            else:
                new_user = Credentials(username=username, password=generate_password_hash(
                password1, method='sha256'), role = 1)

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)

            flash('Account created!', category='success')
            if (role == "user"):
                return redirect(url_for('user_main'))
            else:
                return redirect(url_for('organizer_main'))

    return render_template('register.html', form=form)

@app.route('/user', methods=['GET'])
def user_main():
    return render_template('user_main.html')

@app.route('/organizer', methods=['GET'])
def organizer_main():
    return render_template('organizer_main.html')
