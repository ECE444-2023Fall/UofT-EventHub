from flask import (
    Blueprint,
    render_template,
    abort,
)
from flask_login import login_required, current_user

from app.main import db
from app.globals import FILTERS, EVENT_CATEGORIES
from app.auth import login_required, user_required
from app.database import EventRegistration, EventDetails
from app.search import get_eventids_matching_search_query
from app.filter import filter_for_today_events, filter_for_inperson_events, filter_for_free_events, filter_events_on_category, filter_events_on_event_ids_list, filter_for_past_events

user_events = Blueprint("user_events", __name__)

@user_events.route("/myevents/", methods=["GET"])
@user_events.route("/myevents/<filter>", methods=["GET"])
@user_events.route("/myevents/<filter>/<search>", methods=["GET"])
@login_required
@user_required
def main(filter="all", search=None):
    dict_of_events_details = get_users_events_from_database()

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
    elif filter == "past events":
        dict_of_events_details =  filter_for_past_events(events=dict_of_events_details)
    elif filter != "all":
        if filter.capitalize() not in EVENT_CATEGORIES:
            abort(404, description = {
                "type": "invalid_filter",
                "caller": "user.main",
                "message": f"Invalid filter category {filter}"
            })
        dict_of_events_details = filter_events_on_category(events=dict_of_events_details, category=filter)

    return render_template("user_events.html", event_data=dict_of_events_details, search=search, filter=filter, filter_tags=FILTERS)


def get_users_events_from_database():
    #Query below gets the list of events that the current user has registered for
    events_data = (
        db.session.query(EventDetails)
        .join(EventRegistration)
        .filter(EventRegistration.attendee_username == current_user.username)
    )

    ## Make a dict for event details
    dict_of_events_details = {}
    for row in events_data:
        event_detail = {}

        ## TODO: Ideally we should only be passing information that is required by the user_events.html
        for column in row.__table__.columns:
            event_detail[column.name] = str(getattr(row, column.name))

        dict_of_events_details[row.id] = event_detail

    return dict_of_events_details