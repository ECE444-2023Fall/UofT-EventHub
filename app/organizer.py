from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.main import db # db is for database
from app.database import EventDetails, EventBanner, Credentials
from app.auth import organizer_required

organizer = Blueprint("organizer", __name__)


@organizer.route("/organizer", methods=["GET"])
@login_required
@organizer_required
def main():
    my_events_data = (
        db.session.query(EventDetails)
        .join(Credentials)
        .filter(EventDetails.organizer == current_user.username)
    )
    return render_template("organizer_main.html", my_events_data=my_events_data)
