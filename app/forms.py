from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, DateField, TimeField, URLField, FileField
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

class EventCreateForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    description = StringField('Description:')
    type = StringField('Type:')

    # Location and Time information
    venue = StringField('Venue:')
    start_date = DateField('Start Date:')
    end_date = DateField('End Date:')
    start_time = TimeField('Start Time:')
    end_time = TimeField('End Time:')

    # Additional informations
    link = URLField("Link:")
    banner_id = FileField("Event Banner:")
    additional_info = StringField('Additional Information:')