from flask import Blueprint, render_template, abort, session, redirect, url_for
from sqlalchemy import distinct
from datetime import datetime
import logging

from app.globals import FILTERS, EVENT_CATEGORIES
from app.auth import login_required, user_required
from app.database import EventDetails, Credentials
from app.search import get_eventids_matching_search_query
from app.filter import filter_for_today_events, filter_for_inperson_events, filter_for_free_events, filter_events_on_category, filter_events_on_event_ids_list, filter_for_past_events
from app.main import db
import json
import random

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
        if filter.capitalize() not in EVENT_CATEGORIES:
            abort(404, description = {
                "type": "invalid_filter",
                "caller": "user.main",
                "message": f"Invalid filter category {filter}"
            })
        dict_of_events_details = filter_events_on_category(events=dict_of_events_details, category=filter)

    event_data_json = convert_dictionary_to_JSON(dict_of_events_details)

    # NOTE: False - Card view and True - Calendar view
    # Default is set to Card view

    # Get the toggle value stored in the session 
    # OR set it to False by default (if session doesn't have a value)
    toggle = session.get('toggle_value', False)
    session['toggle_value'] = toggle

    return render_template("user_main.html", event_data=dict_of_events_details, event_data_json=event_data_json, 
                           search=search, filter=filter, filter_tags=FILTERS, toggle=toggle)

# This function is used to change the 'toggle_value' value in the session
# while preserving the current filter and search parameters
@user.route('/user/toggle', methods=["POST"])
@user.route("/user/toggle/<filter>", methods=["POST"])
@user.route("/user/toggle/<filter>/<search>", methods=["POST"])
def toggle(filter="all", search=None):
    # Toggle the value and store it in the session
    session['toggle_value'] = not session.get('toggle_value', True)
    return redirect(url_for('user.main', filter=filter, search=search))

# Helper functions for the users main functionalities
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

def convert_dictionary_to_JSON(events):
    event_list = []
    colors = ['#dc3545', '#007bff', '#28a745', '#ffc107', '#17a2b8']
    #right now set to random initialisation, we will modify this to colour dependent on events

    for event_id, event_data in events.items():
        name = event_data['name']
        start_date = event_data['start_date']
        end_date = event_data['end_date']
        start_time = event_data['start_time']
        end_time = event_data['end_time']
        
        background_color = random.choice(colors)
        border_color = background_color
    
        event_info = {
            'key' : event_id,
            'title': name,
            'start': f'{start_date}T{start_time}',
            'end': f'{end_date}T{end_time}',
            'backgroundColor': background_color,
            'borderColor': border_color
        }
        
        event_list.append(event_info)

    event_data_json = json.dumps(event_list)

    logging.info(event_data_json)
    return event_data_json


# Function for users to view a list of all organizers with upcoming and/or past events
@user.route("/user/organizers", methods=["GET"])
@login_required
@user_required
def view_all_organizers():
    logging.info("Loading webpage for Users to view all Organizers")

    organizers = get_active_organizers()

    return render_template("user_organizers_list.html", organizers=organizers)

# Get only the organizers that have upcoming events or had events in the past
def get_active_organizers():

    # Joining EventDetails and Credentials tables, and selecting only distinct organizer usernames and names
    organizers = db.session.query(Credentials.username, Credentials.name).join(
        EventDetails, Credentials.username == EventDetails.organizer
    ).distinct().all()

    return organizers

# Function for users to view individual organizer pages including upcoming and/or past events
@user.route("/user/organizers/<organizer_username>", methods=["GET"])
@login_required
@user_required
def view_organizer(organizer_username):
    logging.info("Loading webpage for Organizer: %s", organizer_username)

    organizer_name = EventDetails.get_organizer_name_from_username(organizer_username)
    
    # Get the upcoming and past events from the current time
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
