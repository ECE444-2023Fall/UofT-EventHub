from main import db

class Credentials(db.Model):
    username = db.Column(db.String(150), primary_key=True)
    password = db.Column(db.String(150))
    role = db.Column(db.Integer)