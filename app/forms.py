from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email

R_USER = "user"
R_ORGANIZER = "organizer"

class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegForm(FlaskForm):
    role = SelectField('Role:', choices=[(R_USER, 'User'), (R_ORGANIZER, 'Organizer')], validators=[DataRequired()])
    username = StringField('Username:', validators=[DataRequired()])
    password1 = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')