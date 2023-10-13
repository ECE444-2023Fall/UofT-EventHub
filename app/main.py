from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from forms import LoginForm, RegForm
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app(debug):
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = '4829jfnwurduh4293k'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    bootstrap = Bootstrap(app=app)
    moment = Moment(app)

    from models import Credentials

    with app.app_context():
        db.create_all()

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
        user = Credentials.query.filter_by(username=username).first()
        if user:
            if (user.password == password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')

            # if check_password_hash(user.password, password):
            #     flash('Logged in successfully!', category='success')
            #     login_user(user, remember=True)
            #     return redirect(url_for('views.home'))
            # else:
            #     flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

        # Attempt redirection
        # if role == R_USER:
        #     return redirect(url_for('user_main'))
        # else:
        #     return redirect(url_for('organizer_main'))
        return redirect(url_for('user_main'))
        
        print(f"Entered Data: ({username}, {password})")

        return redirect((url_for('login')))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if form.validate_on_submit():
        role = form.role.data
        username = form.username.data
        password = form.password.data
        # Authenticate the entry
        # user = User.query.filter_by(username=username).first()
        # if user:
        #     if check_password_hash(user.password, password):
        #         flash('Logged in successfully!', category='success')
        #         login_user(user, remember=True)
        #         return redirect(url_for('views.home'))
        #     else:
        #         flash('Incorrect password, try again.', category='error')
        # else:
        #     flash('Email does not exist.', category='error')

        print(f"Entered Data: ({username}, {password}, {role})")

        if role == R_USER:
            return redirect(url_for('user_main'))
        else:
            return redirect(url_for('organizer_main'))

    return render_template('login.html', form=form)

@app.route('/user', methods=['GET'])
def user_main():
    return render_template('user_main.html')

@app.route('/organizer', methods=['GET'])
def organizer_main():
    return render_template('organizer_main.html')
