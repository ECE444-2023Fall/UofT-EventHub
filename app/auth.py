from flask import Blueprint, render_template, flash, redirect, url_for, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import logging

from app.globals import Role
from app.main import db
from app.forms import LoginForm, RegForm
from app.database import Credentials

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET", "POST"])
def login():
    if hasattr(current_user, "role") and current_user.role == Role.USER.value:
        return redirect(url_for("user.main"))
    elif hasattr(current_user, "role") and current_user.role == Role.ORGANIZER.value:
        return redirect(url_for("organizer.main"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Authenticate the entry
        logging.info("Entered Data: (%s, %s)", username, password)
        user = Credentials.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="primary")
                login_user(user, remember=True)

                # Redirection to the correct home page
                if user.role == Role.USER.value:
                    return redirect(url_for("user.main"))
                else:
                    return redirect(url_for("organizer.main"))
            else:
                flash("Incorrect password, try again.", category="danger")
        else:
            flash("Username does not exist.", category="danger")

    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegForm()
    if form.validate_on_submit():
        role = int(form.role.data)
        name = form.name.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        # Authenticate the entry of a new user and add it to the database
        user = Credentials.query.filter_by(username=username).first()
        if len(name) < 1:
            flash("Name must be greater than 1 character.", category="warning")
        elif user:
            flash("Username already exists.", category="warning")
        elif len(username) < 4:
            flash("Username must be greater than 3 characters.", category="warning")
        elif password1 != password2:
            flash("Passwords don't match.", category="danger")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="danger")
        else:
            logging.info("Entered Data: (%s, %s, %s)", username, password1, role)
            new_user = Credentials(
                name=name,
                username=username,
                password=generate_password_hash(password1, method="sha256"),
                role=role,
            )
            
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)

            flash("Account created!", category="primary")
            if role == Role.USER.value:
                # Redirect the user to fill additional details
                return redirect(url_for("account.add_user_details"))
            else:
                # Redirect the organizer to their landing page
                return redirect(url_for("organizer.main"))

    return render_template("register.html", form=form)


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != Role.USER.value:
            abort(401, description = {
                "type": "user_unauthorized",
                "caller": "user_required",
                "message": "You need to be a user to access this page"
            })
        return f(*args, **kwargs)

    return decorated_function


def organizer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != Role.ORGANIZER.value:
            abort(401, description = {
                "type": "organizer_unauthorized",
                "caller": "organizer_required",
                "message": "You need to be a organizer to access this page"
            })
        return f(*args, **kwargs)

    return decorated_function
