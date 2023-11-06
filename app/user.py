from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.globals import FILTERS
from app.auth import login_required, user_required
from app.database import EventDetails, EventRating
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

    ## Make a dict for event details
    dict_of_events_details = {}
    for row in events_data:
        event_detail = {}

        ## TODO: Ideally we should only be passing information that is required by the user_main.html
        for column in row.__table__.columns:
            event_detail[column.name] = str(getattr(row, column.name))

        dict_of_events_details[row.id] = event_detail

    return dict_of_events_details
    # # only for testing to see if user inputs for ratings are actually being stored in the database:
    # events_ratings = EventRating.query.all()
    # return render_template('user_main.html', events_data=events_data, events_ratings = events_ratings)

@user.route('/submit_rating', methods=['POST'])
def submit_rating():
    # Get the user's username (assuming they are logged in)
    #TODO: add user info to rating if need be
    # user_username = 

    event_id = request.form.get('event_id')
    rating = request.form.get('rating')

    if event_id and rating: #and user_username 
        # Check if the user has already rated this event, and update the rating if they have
        # existing_rating = EventRating.query.filter_by(event_id=event_id).first()
        # if existing_rating:
        #     existing_rating.rating = rating
        # else:
        # Create a new rating record
        event_rating = EventRating(event_id=event_id, rating=rating)
        db.session.add(event_rating)
        
        db.session.commit()

        flash('Rating submitted successfully', 'success')
    else:
        flash('Failed to submit rating. Please try again.', 'error')
    
    return redirect(url_for('user.main'))