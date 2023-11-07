from flask_login import UserMixin
from sqlalchemy import ForeignKey

from app.main import db


class Credentials(db.Model, UserMixin):
    __tablename__ = "credentials"

    username = db.Column(db.String(150), primary_key=True)
    password = db.Column(db.String(150))
    role = db.Column(db.Integer)  # 0: User, 1: Organizer

    # A sample data from this table will look like this
    def __repr__(self):
        return (
            f"Username : {self.username}, Password: {self.password}, Role: {self.role}"
        )

    def get_id(self):
        return self.username


class EventDetails(db.Model):
    __tablename__ = "event_details"

    # Event Indetifier information
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(1000))
    category = db.Column(db.String(150))
    organizer = db.Column(db.String(150), ForeignKey("credentials.username"))

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

    # Additional informations
    redirect_link = db.Column(db.String(300))
    additional_info = db.Column(db.String(1000))

    # A sample data from this table will look like this
    def __repr__(self):
        return f"ID : {self.id}, Name: {self.name}, Organizer: {self.organizer}"

    def get_id(self):
        return self.id


class EventBanner(db.Model):
    __tablename__ = "event_banners"

    # Event Indetifier information
    # TODO: If we are restricting one graphics per event we can remove id and make event_id a primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, ForeignKey("event_details.id"))
    image = db.Column(db.String(250), nullable=True)

    # A sample data from this table will look like this
    def __repr__(self):
        return f"Event ID : {self.id}, Banner Image: {self.name}"

    def get_id(self):
        return self.event_id


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


class UserDetails(db.Model):
    __tablename__ = "user_details"

    # Basic user details we will need for registration
    username = db.Column(db.String(150), primary_key=True)
    firstname = db.Column(db.String(250), nullable=False)
    lastname = db.Column(db.String(250), nullable=True)
    email = db.Column(db.String(250), nullable=False)

    # A sample data from this table will look like this
    def __repr__(self):
        return f"Username : {self.username}, First name: {self.firstname}, Email: {self.email}"
