from app.main import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey

class Credentials(db.Model, UserMixin):
    __tablename__ = 'credentials'

    username = db.Column(db.String(150), primary_key=True)
    password = db.Column(db.String(150))
    role = db.Column(db.Integer) # 0: User, 1: Organizer

    # A sample data from this table will look like this
    def __repr__(self):
        return f"Username : {self.username}, Password: {self.password}, Role: {self.role}"
    
    def get_id(self):
        return (self.username)
    
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name

event_tags = db.Table('event_tags',
    db.Column('event_id', db.Integer, db.ForeignKey('event_details.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class EventDetails(db.Model):
    __tablename__ = 'event_details'
    # Event Indetifier information
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(1000))
    type = db.Column(db.String(150))

    # Location and Time information
    venue = db.Column(db.String(150))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    # Additional informations
    link = db.Column(db.String(300))
    banner_id = db.Column(db.Integer)
    additional_info = db.Column(db.String(1000))

    # Add a relationship to the tags
    tags = db.relationship('Tag', secondary=event_tags, backref=db.backref('events', lazy='dynamic'))

    # A sample data from this table will look like this
    def __repr__(self):
        return f"ID : {self.id}, Name: {self.name}, Tags: {', '.join(tag.name for tag in self.tags)}"
    
    def get_id(self):
        return (self.id)
    
class OrganizerEventDetails(db.Model):
    __tablename__ = 'organizer_event_relations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, ForeignKey('event_details.id'))
    organizer_username = db.Column(db.String(150), ForeignKey('credentials.username'))

    # A sample data from this table will look like this
    def __repr__(self):
        return f"Organizer: {self.organizer_name}, Event ID: {self.event_id}"
