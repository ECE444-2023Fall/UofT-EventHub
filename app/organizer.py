from flask import Blueprint, render_template, request, flash, redirect, url_for, Flask, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager
from forms import LoginForm, RegForm, EventCreateForm

from main import db
from database import Credentials

organizer = Blueprint('organizer', __name__)

@organizer.route('/organizer/create_event', methods=['GET', 'POST'])
def create_event():
    form = EventCreateForm()

    if form.validate_on_submit():
        pass

    return render_template('create_event.html', form=form)