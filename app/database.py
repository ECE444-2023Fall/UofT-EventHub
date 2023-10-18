from main import db
from flask_login import UserMixin, LoginManager
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

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
    
class EventDetails(db.Model, UserMixin):
    __tablename__ = 'event_details'
    # Event Indetifier information
    id = db.Column(db.Integer, primary_key=True)
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

    # A sample data from this table will look like this
    def __repr__(self):
        return f"ID : {self.id}, Name: {self.name}"
    
    def get_id(self):
        return (self.id)