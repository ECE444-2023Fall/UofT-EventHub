from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    SelectField,
    DateField,
    TimeField,
    URLField,
    FileField,
    TextAreaField,
    BooleanField,
    FloatField,
    IntegerField,
)
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, NumberRange

from app.globals import Role, EVENT_CATEGORIES

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Log In")


class RegForm(FlaskForm):
    role = SelectField(
        "Role:",
        choices=[(Role.USER.value, "User"), (Role.ORGANIZER.value, "Organizer")],
        validators=[DataRequired()],
    )
    username = StringField("Username:", validators=[DataRequired()])
    password1 = PasswordField("Password:", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EventCreateForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    description = StringField("Description:")
    category = SelectField(
        "Category:", 
        choices=EVENT_CATEGORIES, 
        validators=[DataRequired()]
    )

    # Location and Time information
    is_online = BooleanField("Is this an online event?")
    venue = StringField("Venue:")
    start_date = DateField("Start Date:")
    end_date = DateField("End Date:")
    start_time = TimeField("Start Time:")
    end_time = TimeField("End Time:")

    # Participant capacity information
    max_capacity = IntegerField(
        "Capacity of your event:", validators=[NumberRange(min=0)])

    # Ticket Price Information
    ticket_price = FloatField("Ticket Price:", default=0.0)

    # Additional informations
    redirect_link = URLField("Registration Redirect Link:")
    banner_image = FileField(
        "Image:", validators=[FileAllowed(["png"], "PNG Images only!")]
    )
    additional_info = TextAreaField("Additional Information:")
    
    # Tags
    tags = StringField('Tags (Comma-separated)')

    submit = SubmitField("Submit")
