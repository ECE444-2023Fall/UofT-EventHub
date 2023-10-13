from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email
from enum import Enum

from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '4829jfnwurduh4293k'
bootstrap = Bootstrap(app=app)
moment = Moment(app)

R_USER = "user"
R_ORGANIZER = "organizer"

class NameForm(FlaskForm):
    # NOTE: In the future the role will be infered after authorization
    role = SelectField('Role:', choices=[(R_USER, 'User'), (R_ORGANIZER, 'Organizer')], validators=[DataRequired()])
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def login():
    form = NameForm()
    if form.validate_on_submit():
        role = form.role.data
        username = form.username.data
        password = form.password.data
        # Authenticate the entry

        # Attempt redirection
        if role == R_USER:
            return redirect(url_for('user_main'))
        else:
            return redirect(url_for('organizer_main'))
        
        print(f"Entered Data: ({role}, {username}, {password})")

        return redirect((url_for('login')))
    return render_template('login.html', form=form)

@app.route('/user', methods=['GET'])
def user_main():
    return render_template('user_main.html')

@app.route('/organizer', methods=['GET'])
def organizer_main():
    return render_template('organizer_main.html')
