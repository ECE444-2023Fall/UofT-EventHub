from flask import Blueprint, render_template

from app.auth import login_required, user_required
from app.database import EventDetails

user = Blueprint("user", __name__)


@user.route("/user", methods=["GET"])
@login_required
@user_required
def main():
    events_data = EventDetails.query.all()

    ## Make a dict for event details
    dict_of_events_details = {}
    for row in events_data:
        event_detail = {}

        ## TODO: Ideally we should only be passing information that is required by the user_main.html
        for column in row.__table__.columns:
            event_detail[column.name] = str(getattr(row, column.name))

        dict_of_events_details[row.id] = event_detail

    return render_template("user_main.html", event_data=dict_of_events_details)
