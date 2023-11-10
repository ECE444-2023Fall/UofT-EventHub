from flask import Blueprint, render_template
from sqlalchemy import distinct
from datetime import datetime
import logging

from app.globals import FILTERS
from app.auth import login_required, user_required
from app.database import EventDetails, Credentials
from app.search import get_eventids_matching_search_query
from app.filter import filter_for_today_events, filter_for_inperson_events, filter_for_free_events, filter_events_on_category, filter_events_on_event_ids_list, filter_for_past_events
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
    elif filter == "past events":
        dict_of_events_details =  filter_for_past_events(events=dict_of_events_details)
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
    logging.info("Loading webpage for Users to view all Organizers")

    organizers = get_active_organizers()

    return render_template("user_organizers_list.html", organizers=organizers)

# Get only the organizers that have upcoming events or had events in the past
def get_active_organizers():

    # Joining EventDetails and Credentials tables
    # Selecting only distinct organizer usernames and names
    organizers = db.session.query(Credentials.username, Credentials.name).join(
        EventDetails, Credentials.username == EventDetails.organizer
    ).distinct().all()

    return organizers

@user.route("/user/organizers/<organizer_username>", methods=["GET"])
@login_required
@user_required
def view_organizer(organizer_username):
    logging.info("Loading webpage for Organizer: %s", organizer_username)

    organizer_name = EventDetails.get_organizer_name_from_username(organizer_username)
    
    upcoming_events = get_organizer_upcoming_events(organizer_username)
    past_events = get_organizer_past_events(organizer_username)

    return render_template("user_organizer_page.html", organizer_name=organizer_name, upcoming_events=upcoming_events, past_events=past_events)

# Get the upcoming events for an organizer
def get_organizer_upcoming_events(organizer_username):
    # Get the current date and time to filter for upcoming events
    current_date = datetime.now().date()
    current_time = datetime.now().time()

    # Querying events where the organizer is the specified username and the event is yet to start (upcoming)
    upcoming_events = (
        EventDetails.query
        .filter_by(organizer=organizer_username)
        .filter(
            db.or_(
                EventDetails.start_date > current_date,
                db.and_(
                    EventDetails.start_date == current_date,
                    EventDetails.start_time > current_time
                )
            )
        )
        .all()
    )

    return upcoming_events

# Get the past events for an organizer
def get_organizer_past_events(organizer_username):
    # Get the current date and time to filter for past events
    current_date = datetime.now().date()
    current_time = datetime.now().time()

    # Querying events where the organizer is the specified username and the event has already started (past)
    past_events = (
        EventDetails.query
        .filter_by(organizer=organizer_username)
        .filter(
            db.or_(
                EventDetails.start_date < current_date,
                db.and_(
                    EventDetails.start_date == current_date,
                    EventDetails.start_time < current_time
                )
            )
        )
        .all()
    )

    return past_events
