from flask_login import UserMixin
from sqlalchemy import ForeignKey
from icalendar import Calendar, Event
from datetime import datetime

from app.main import db

class Credentials(db.Model, UserMixin):
    __tablename__ = "credentials"

    username = db.Column(db.String(150), primary_key=True)
    role = db.Column(db.Integer)  # 0: User, 1: Organizer
    password = db.Column(db.String(150))
    name  = db.Column(db.String(150))

    # A sample data from this table will look like this
    def __repr__(self):
        return (
            f"Username : {self.username}, Password: {self.password}, Role: {self.role}, Name: {self.name}"
        )

    def get_id(self):
        return (self.username)

class UserDetails(db.Model, UserMixin):
    __tablename__ = "user_details"

    username = db.Column(db.String(150), ForeignKey("credentials.username"), primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    year = db.Column(db.String(150))
    course_type = db.Column(db.String(150))
    department = db.Column(db.String(150))
    campus = db.Column(db.String(150))
    email = db.Column(db.String(150))

    # A sample data from this table will look like this
    def __repr__(self):
        return (
            f"Username : {self.username}, First name: {self.firstname}, Last name: {self.lastname}"
        )

    def get_id(self):
        return (self.username)

# Defining the Tag model to be used to store event tags
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name

# Defining the association table for the many-to-many relationship between EventDetails and Tag
event_tags = db.Table('event_tags',
    db.Column('event_id', db.Integer, db.ForeignKey('event_details.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class EventDetails(db.Model):
    __tablename__ = "event_details"

    # Event Indentifier information
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    short_description = db.Column(db.String(100))
    long_description = db.Column(db.String(1000))
    category = db.Column(db.String(150))
    organizer = db.Column(db.String(150), ForeignKey("credentials.username"))

    # Event banner information
    image = db.Column(db.String(250), nullable=True)

    # Location and Time information
    is_online = db.Column(db.Integer)
    venue = db.Column(db.String(150))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    # Participant capacity information
    max_capacity = db.Column(db.Integer)
    current_capacity = db.Column(db.Integer)

    # Ticket Price Information
    ticket_price = db.Column(db.Float)

    # Additional information
    redirect_link = db.Column(db.String(300))
    additional_info = db.Column(db.String(1000))

    # Add a relationship to the tags
    tags = db.relationship('Tag', secondary=event_tags, backref=db.backref('events', lazy='dynamic'))

    # A sample data from this table will look like this
    def __repr__(self):
        return f"ID : {self.id}, Name: {self.name}, Organizer: {self.organizer}, Tags: {', '.join(tag.name for tag in self.tags)}"

    def get_id(self):
        return self.id
    
    # Method to get the Organizer's name without having to directly access Credentials table otherwise
    def get_organizer_name_from_username(organizer_username):
        organizer = Credentials.query.filter_by(username=organizer_username).first()
        return organizer.name if organizer else None
    
    # Method to create am iCal event using the information in the event details
    def to_ical_event(self):
        cal = Calendar()
        event = Event()

        event.add('summary', self.name)
        event.add('description', self.short_description)
        event.add('location', self.venue)

        # Set the event start and end time
        start_datetime = datetime.combine(self.start_date, self.start_time)
        end_datetime = datetime.combine(self.end_date, self.end_time)

        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)

        cal.add_component(event)
        return cal.to_ical()

class EventRating(db.Model):
    __tablename__ = 'event_ratings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #username of the user who gave the rating:
    attendee_username = db.Column(db.String(150), ForeignKey("credentials.username"))
    # Event on which the rating was given for:
    event_id = db.Column(db.Integer, ForeignKey('event_details.id'))
    #the rating:
    #TODO: Perhaps limit the range of integers from 1 to 5
    rating = db.Column(db.Integer)

    def __repr__(self):
        return f"Username: {self.attendee_username}, ID : {self.event_id}, Rating: {self.rating}"

class EventRegistration(db.Model):
    __tablename__ = "event_registration"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, ForeignKey("event_details.id"), nullable=False)
    attendee_username = db.Column(db.String(150), ForeignKey("credentials.username"), nullable=False)

    # Unique constraint
    __table_args__ = (db.UniqueConstraint("event_id", "attendee_username"),)

    # A sample data from this table will look like this
    def __repr__(self):
        return f"Attendee: {self.attendee_username}, Event ID: {self.event_id}"
