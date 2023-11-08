from flask import Blueprint, render_template

from app.globals import FILTERS
from app.auth import login_required, user_required
from app.database import EventDetails, OrganizerEventDetails
from app.search import get_eventids_matching_search_query
from app.filter import filter_for_today_events, filter_for_inperson_events, filter_for_free_events, filter_events_on_category, filter_events_on_event_ids_list
from app.main import db


from sqlalchemy import distinct

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


"""@user.route("/user/organizers", methods=["GET"])
@login_required
@user_required
def view_organizers():
    organizer_usernames = get_organizers()
    
    # Create a string with organizer usernames as headings
    organizer_headings = "<h1>Organizer Usernames:</h1>"
    for username in organizer_usernames:
        organizer_headings += f"<h2>{username}</h2>"
    
    ###return organizer_headings
    return render_template("user_organizers.html")

# Get all organizers that have/had upcoming/past events
def get_organizers():
    
    # Query the database to get a list of all organizer usernames with upcoming/past events
    organizers = OrganizerEventDetails.query.with_entities(distinct(OrganizerEventDetails.organizer_username)).all()
    
    # Extracting the usernames from the query results
    organizer_usernames = [organizer[0] for organizer in organizers]
    
    return organizer_usernames"""

from app.main import db

@user.route("/user/organizers", methods=["GET"])
@login_required
@user_required
def view_organizers():
    organizer_usernames = get_distinct_organizers()
    return render_template("user_organizers.html", organizer_usernames=organizer_usernames)

def get_distinct_organizers():
    # Join OrganizerEventDetails and EventDetails tables
    query = (
        db.session.query(OrganizerEventDetails.organizer_username)
        .join(EventDetails, OrganizerEventDetails.event_id == EventDetails.id)
        .distinct()
    )

    # Execute the query and get distinct organizer usernames
    organizer_usernames = [result[0] for result in query.all()]

    return organizer_usernames