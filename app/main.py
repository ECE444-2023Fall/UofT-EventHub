from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email

from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '4829jfnwurduh4293k'
bootstrap = Bootstrap(app=app)
moment = Moment(app)

class NameForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    email = StringField('UofT Email address:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def login():
    form = NameForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        print(f"Entered Data: ({username}, {email}, {password})")
        # Authenticate the entry
        # Attempt redirection

        # NOTE: currently I am redirecting to the login page (Will remove in the future)
        return redirect((url_for('login')))
    return render_template('login.html', form=form)
