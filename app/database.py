from main import db
from flask_login import UserMixin, LoginManager

class Credentials(db.Model, UserMixin):
    username = db.Column(db.String(150), primary_key=True)
    password = db.Column(db.String(150))
    role = db.Column(db.Integer) # 0: User, 1: Organizer

    # A sample data from this table will look like this
    def __repr__(self):
        return f"Username : {self.username}, Password: {self.password}, Role: {self.role}"
    
    def get_id(self):
        return (self.username)