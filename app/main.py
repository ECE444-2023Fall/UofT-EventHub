from flask import Flask, render_template, session, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy

## Initialize and import databases schemas
db = SQLAlchemy()
from database import Credentials, EventDetails

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

    ## Register the auth path so that we can use the routes defined there. E.g. Login and Register
    from auth import auth
    from user import user
    from organizer import organizer
    from events import events
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(user, url_prefix='/')
    app.register_blueprint(organizer, url_prefix='/')
    app.register_blueprint(events, url_prefix='/')

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
