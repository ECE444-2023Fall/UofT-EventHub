from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.main import db # db is for database
from app.database import EventDetails, Credentials
from app.auth import organizer_required
from app.analytics import get_avg_rating

organizer = Blueprint("organizer", __name__)


@organizer.route("/organizer", methods=["GET"])
@login_required
@organizer_required
def main():
    my_events_data = get_my_events_from_database()
    my_avg_rating = get_avg_rating()

    return render_template("organizer_main.html", my_events_data=my_events_data, my_avg_rating=my_avg_rating)

def get_my_events_from_database():
    events_data = (
        db.session.query(EventDetails)
        .join(Credentials)
        .filter(EventDetails.organizer == current_user.username)
        .all()
    )

    # Make a dict for event details
    dict_of_events_details = {}
    for row in events_data:
        event_detail = {}

        # TODO: Ideally we should only be passing information that is required by the user_main.html
        for column in row.__table__.columns:
            event_detail[column.name] = str(getattr(row, column.name))

        dict_of_events_details[row.id] = event_detail

    return dict_of_events_details
