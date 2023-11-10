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
    EmailField,
)
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, NumberRange, Email, Length

from app.globals import (
    Role, 
    EVENT_CATEGORIES, 
    YEAR_CATEGORIES, 
    COURSE_CATEGORIES,
    DEPARTMENT_CATEGORIES,
    CAMPUS_CATEGORIES
)

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
    name = StringField("Name:", validators=[DataRequired()])
    username = StringField("Username:", validators=[DataRequired()])
    password1 = PasswordField("Password:", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EventCreateForm(FlaskForm):
    name = StringField("Name*:", validators=[DataRequired()])
    short_description = StringField("Short Description* (Max 90 characters):", validators=[DataRequired(), Length(max=90, message="Please keep the description under 90 characters")])
    long_description = StringField("Long Description (Optional):")
    category = SelectField(
        "Category:", 
        choices=EVENT_CATEGORIES, 
        validators=[DataRequired()]
    )

    # Location and Time information
    is_online = BooleanField("Is this an online event?")
    venue = StringField("Venue:")
    start_date = DateField("Start Date*:")
    end_date = DateField("End Date*:")
    start_time = TimeField("Start Time*:")
    end_time = TimeField("End Time*:")

    # Participant capacity information
    max_capacity = IntegerField(
        "Capacity of the event:", validators=[NumberRange(min=0)])

    # Ticket Price Information
    ticket_price = FloatField("Ticket Price:", default=0.0, validators=[NumberRange(min=0.0)])

    # Additional informations
    redirect_link = URLField("External Registration Link (Optional) :")
    banner_image = FileField(
        "Image:", validators=[FileAllowed(["png"], "Please upload a PNG image.")]
    )
    additional_info = TextAreaField("Additional Information:")
    
    # Tags
    tags = StringField('Tags (Comma-separated)')

    submit = SubmitField("Submit")

class UserDetailsForm(FlaskForm):
    firstname = StringField("First name:", validators=[DataRequired()])
    lastname = StringField("Last name:", validators=[DataRequired()])
    year = SelectField(
        "Year:", 
        choices=YEAR_CATEGORIES, 
        validators=[DataRequired()]
    )
    course_type = SelectField(
        "Affiliation:", 
        choices=COURSE_CATEGORIES, 
        validators=[DataRequired()]
    )
    department = SelectField(
        "Department:", 
        choices=DEPARTMENT_CATEGORIES, 
        validators=[DataRequired()]
    )
    campus = SelectField(
        "Campus:", 
        choices=CAMPUS_CATEGORIES, 
        validators=[DataRequired()]
    )
    email = EmailField('Email address', validators=[DataRequired(), Email()])

    submit = SubmitField("Save")

class UserRegisterForm(FlaskForm):
    firstname = StringField("First name:", validators=[DataRequired()])
    lastname = StringField("Last name:", validators=[DataRequired()])
    year = SelectField(
        "Year:", 
        choices=YEAR_CATEGORIES, 
        validators=[DataRequired()]
    )
    course_type = SelectField(
        "Affiliation:", 
        choices=COURSE_CATEGORIES, 
        validators=[DataRequired()]
    )
    department = SelectField(
        "Department:", 
        choices=DEPARTMENT_CATEGORIES, 
        validators=[DataRequired()]
    )
    campus = SelectField(
        "Campus:", 
        choices=CAMPUS_CATEGORIES, 
        validators=[DataRequired()]
    )
    email = EmailField('Email address', validators=[DataRequired(), Email()])

    submit = SubmitField("Submit")