from flask import Blueprint, render_template

from app.globals import FILTERS
from app.auth import login_required, user_required
from app.database import EventDetails
from app.search import func_search_events
from app.filter import func_filter_events


user = Blueprint("user", __name__)


@user.route("/user/", methods=["GET"])
@user.route("/user/<filter>", methods=["GET"])
@user.route("/user/<filter>/<search>", methods=["GET"])
@login_required
@user_required
def main(filter="all", search=None):
    dict_of_events_details = {}
    if search == None:
        dict_of_events_details = get_all_events_from_database()
    else:
        dict_of_events_details = func_search_events(query=search)
    
    # Filter the events list
    if filter != "tags":
        dict_of_events_details = func_filter_events(events=dict_of_events_details, tag=filter)

    return render_template("user_main.html", event_data=dict_of_events_details, search=search, filter=filter, filter_tags=FILTERS)

def get_all_events_from_database():
    events_data = EventDetails.query.all()

    ## Make a dict for event details
    dict_of_events_details = {}
    for row in events_data:
        event_detail = {}

        ## TODO: Ideally we should only be passing information that is required by the user_main.html
        for column in row.__table__.columns:
            event_detail[column.name] = str(getattr(row, column.name))

        dict_of_events_details[row.id] = event_detail

    return dict_of_events_details