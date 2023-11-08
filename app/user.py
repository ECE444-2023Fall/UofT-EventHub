from flask import Blueprint, render_template
from sqlalchemy import distinct

from app.globals import FILTERS
from app.auth import login_required, user_required
from app.database import EventDetails, Credentials
from app.search import get_eventids_matching_search_query
from app.filter import filter_for_today_events, filter_for_inperson_events, filter_for_free_events, filter_events_on_category, filter_events_on_event_ids_list
from app.main import db

user = Blueprint("user", __name__)


@user.route("/user/", methods=["GET"])
@user.route("/user/<filter>", methods=["GET"])
@user.route("/user/<filter>/<search>", methods=["GET"])
@login_required
@user_required
def main(filter="all", search=None):
    dict_of_events_details = get_all_events_from_database()

    # Filter the events list based on the search query
    if search != None:
        list_event_ids = get_eventids_matching_search_query(query=search)
        dict_of_events_details = filter_events_on_event_ids_list(events=dict_of_events_details, event_ids=list_event_ids)

    # Filter the events list based on the filter tags
    if filter == "in-person":
        dict_of_events_details = filter_for_inperson_events(events=dict_of_events_details)
    elif filter == "free":
        dict_of_events_details = filter_for_free_events(events=dict_of_events_details)
    elif filter == "today":
        dict_of_events_details = filter_for_today_events(events=dict_of_events_details)
    elif filter != "all":
        dict_of_events_details = filter_events_on_category(events=dict_of_events_details, category=filter)

    return render_template("user_main.html", event_data=dict_of_events_details, search=search, filter=filter, filter_tags=FILTERS)

def get_all_events_from_database():
    events_data = EventDetails.query.all()

    # Make a dict for event details
    dict_of_events_details = {}
    for row in events_data:
        event_detail = {}

        # TODO: Ideally we should only be passing information that is required by the user_main.html
        for column in row.__table__.columns:
            event_detail[column.name] = str(getattr(row, column.name))

        dict_of_events_details[row.id] = event_detail

    return dict_of_events_details


@user.route("/user/organizers", methods=["GET"])
@login_required
@user_required
def view_all_organizers():
    organizers = get_active_organizers()
    return render_template("user_organizers.html", organizers=organizers)

# Get only the organizers that have upcoming events or had past events
def get_active_organizers():

    # Joining EventDetails and Credentials tables
    # Selecting only distinct organizer usernames and names
    organizers = db.session.query(Credentials.username, Credentials.name).join(
        EventDetails, Credentials.username == EventDetails.organizer
    ).distinct().all()

    return organizers
