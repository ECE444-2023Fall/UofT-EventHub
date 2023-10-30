from flask import Blueprint, render_template

from app.auth import login_required
from app.database import EventDetails

user = Blueprint('user', __name__)

@user.route('/user', methods=['GET'])
@login_required
def main():
    events_data = EventDetails.query.all()
    return render_template('user_main.html', events_data=events_data)
