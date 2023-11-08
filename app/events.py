from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    flash,
    current_app,
    redirect,
    url_for,
    abort,
)
from flask_login import login_required, current_user
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from datetime import date
import os.path
import os

from app.main import db # db is for database
from app.globals import Role
from app.auth import organizer_required
from app.database import Credentials, EventRegistration, EventDetails, EventBanner, EventRating
from app.forms import EventCreateForm

events = Blueprint("events", __name__)


@events.route("/events/<int:id>", methods=["GET"])
@login_required
def show_event(id):
    logging.info("Loading webpage for event ID: %d", id)

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        logging.info(
            "Integrity Error: The event ID passed to show_event has no valid entry in the database"
        )
        abort(404, {
            "type": "event_not_found",
            "caller": "show_event",
            "message": "Can not show the event since the event does not exist"
        })

    # Check if the user registered for the event
    is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=id).first()

    #Check for past event. Users will only be able to rate if this is met. 
    is_past_event = past_event(id)
    logging.info("is it a past event: ",is_past_event)

    #get existing user rating
    prev_rating = previous_rating(attendee_username=current_user.get_id(), event_id=id)
    logging.info("Prev Rating: ", prev_rating)

    event_dict = event.__dict__
    
    # Fix: Need to pass event ID as a string
    str_id = str(event_dict["id"])
    event_dict["id"] = str_id

    if is_registered is not None:
        flash("You are already registered for the event!", category="info")
        return render_template("event.html", event=event_dict, is_registered=True, is_past_event = is_past_event, prev_rating=prev_rating)
    else:
        return render_template("event.html", event=event_dict, is_registered=False, is_past_event = is_past_event, prev_rating=prev_rating)


@events.route("/events/admin/<int:id>", methods=["GET"])
@login_required
@organizer_required
def show_event_admin(id):
    logging.info("Loading admin webpage for event ID: %d", id)

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        logging.info(
            "Integrity Error: The event ID passed to show_event_admin has no valid entry in the database"
        )
        abort(404, {
            "type": "event_not_found",
            "caller": "show_event_admin",
            "message": "Can not show the event since the event does not exist"
        })

    # Get some analytics data for this event
    registered_users = EventRegistration.query.filter_by(event_id=id).all()
    num_of_registrations = len(registered_users)

    # Fix: Need to pass event ID as a string
    event_dict = event.__dict__
    str_id = str(event_dict["id"])
    event_dict["id"] = str_id

    return render_template("event_admin.html", event=event_dict, num_of_registrations=num_of_registrations)


@events.route("/events/create_event", methods=["GET", "POST"])
@login_required
@organizer_required
def create_event():
    form = EventCreateForm()

    if form.validate_on_submit():
        # Add the event details
        new_event = EventDetails(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data.lower(),
            organizer=current_user.username,
            is_online=form.is_online.data,
            venue=form.venue.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            max_capacity=form.max_capacity.data,
            current_capacity=0,
            ticket_price=form.ticket_price.data,
            redirect_link=form.redirect_link.data,
            additional_info=form.additional_info.data,
        )
        db.session.add(new_event)
        db.session.commit()

        add_event_to_index(new_event)

        # Add the banner information for the newly created event
        banner_file = form.banner_image.data
        filename = "event_banner_" + str(new_event.id) + ".png"

        # Save the banner in static/event-assets
        banner_file.save(
            os.path.join(current_app.root_path, "static", "event-assets", filename)
        )

        # Store the path to the banner EventBanner
        event_graphic = EventBanner(event_id=new_event.id, image=filename)

        db.session.add(event_graphic)
        db.session.commit()

        return redirect(url_for("events.show_event_admin", id=new_event.id))

    return render_template("create_event.html", form=form)


@events.route("/events/edit_event/<int:id>", methods=["GET", "POST"])
@login_required
@organizer_required
def edit_event(id):
    logging.info("Loading edit event webpage for event ID: %d", id)

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        logging.info(
            "Integrity Error: The event ID passed to show_event_admin has no valid entry in the database"
        )
        abort(404, {
            "type": "event_not_found",
            "caller": "edit_event",
            "message": "Can not edit the event since the event does not exist"
        })

    # Recreate the Event Form with the default values set
    event_create_form_default = {}
    for field_name, default_value in event.__dict__.items():
        if not hasattr(EventCreateForm, field_name):
            logging.info(f"Form doesn't have attribute: {field_name}")
            continue
        # NOTE: Since we are decapitilizing the category data on form submition,
        # we must perform the opposite operation here
        if field_name == "category":
            default_value = default_value.capitalize()
        event_create_form_default[field_name] = default_value
    logging.info(f"Default Values: {event_create_form_default}")

    form = EventCreateForm(**event_create_form_default)

    if form.validate_on_submit():
        logging.info(f"Edited Event Entries: {form.name.data}, {form.category.data}")
        # Add the event details
        event.name = form.name.data
        event.description = form.description.data
        event.category = form.category.data.lower()
        event.is_online = form.is_online.data
        event.venue = form.venue.data
        event.start_date = form.start_date.data
        event.end_date = form.end_date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        # TODO: Add a check to prevent the max capacity from being set to below the current capacity
        event.max_capacity = form.max_capacity.data
        event.ticket_price = form.ticket_price.data
        event.redirect_link = form.redirect_link.data
        event.additional_info = form.additional_info.data
        db.session.commit()

        # TODO: Update the event details to the index for elastic search

        # Add the banner information for the newly created event
        banner_file = form.banner_image.data
        filename = "event_banner_" + str(event.id) + ".png"

        # Save the banner in static/event-assets
        banner_file.save(
            os.path.join(current_app.root_path, "static", "event-assets", filename)
        )

        # Store the path to the banner EventBanner
        event_graphic = EventBanner.query.filter_by(event_id=event.id).first()
        if event_graphic:
            event_graphic.image = filename
        else:
            event_graphic = EventBanner(event_id=event.id, image=filename)
            db.session.add(event_graphic)

        db.session.commit()

        return redirect(url_for("events.show_event_admin", id=event.id))

    return render_template("create_event.html", form=form)


@events.route("/events/delete_event/<int:id>", methods=["POST"])
@login_required
@organizer_required
def delete_event(id):
    logging.info("Loading edit event webpage for event ID: %d", id)

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        logging.info(
            "Integrity Error: The event ID passed to show_event_admin has no valid entry in the database"
        )
        abort(404, {
            "type": "event_not_found",
            "caller": "delete_event",
            "message": "Can not delete the event since the event does not exist"
        })

    if event.organizer != current_user.username:
        logging.info(f"Current Organizer ({current_user.username} doesn't match the event creator {event.organizer})")
        abort(401, {
            "type": "unauthorized_organizer",
            "caller": "delete_event",
            "message": "You are not authorized to delete this event"
        })

    db.session.delete(event)
    db.session.commit()

    return redirect(url_for("organizer.main"))


@events.route("/events/send_file/<filename>")
@events.route("/events/register/send_file/<filename>")
@login_required
def send_file(filename):
    """
    This function is used to fetch event banner images for event.html pages"
    """

    return send_from_directory(current_app.config["GRAPHIC_DIRECTORY"], filename)


@events.route("/events/register/<int:event_id>", methods=["GET", "POST"])
@login_required
def register_for_event(event_id):
    """
    Description: Responsible for registering the user for an event.
                 Upon succesfull registeration it re-renders the template

    Returns:
        0: On successful registration
        1: If the event ID is invalid
        2: If the username is invalid
        3: If username is valid but the role is organizer
        4: If the user is already registered for the event
        redirect: If the event is a past event
    """
    # Check for valid event ID
    if event_id is None:
        logging.info("Cannot register user with an event ID: None")
        return ("1")

    logging.info("EVENT ID: %s", event_id)
    logging.info("USERNAME: %s", current_user.get_id())

    # Check for valid username
    user = Credentials.query.filter_by(username=current_user.get_id()).first()
    is_past_event = past_event(event_id)
    if not user:
        logging.warning("Cannot register user with an invalid username")
        return ("2")

    # We should also check if a username corresponds to a user and not an organizer
    if user.role != Role.USER.value:
        logging.warning("Cannot register an organizer")
        return ("3")
    
    #Check for past event is also needed and has been implemented on
    #the event.html page where the register button is disabled once an event is over.

    # TODO: Check if event has enough seats left

    # Check if the user is already registered
    is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=event_id).first()
    if is_registered:
        logging.info("Cancelling user's registration")

        # Delete the registeration
        EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=event_id).delete()
        db.session.commit()

        flash("Cancelled registeration for the event!", category="success")
        event = EventDetails.query.filter_by(id=event_id).first()

        return redirect(url_for('events.show_event', id=event_id))

    # Register the user
    new_registration = EventRegistration(
        attendee_username=current_user.get_id(),
        event_id=event_id,
    )

    db.session.add(new_registration)
    db.session.commit()

    flash("Registered for the event!", category="success")
    event = EventDetails.query.filter_by(id=event_id).first()
    return redirect(url_for('events.show_event', id=event_id))

def add_event_to_index(new_event):
    event_detail = {
        "id": new_event.id,
        "name": new_event.name,
        "description": new_event.description,
        "category": new_event.category,
        "venue": new_event.venue,
        "additional_info": new_event.additional_info,
    }

    logging.info("The event dict for indexing:", event_detail)
    es.index(index="events", document=event_detail)
    es.indices.refresh(index="events")
    logging.info(es.cat.count(index="events", format="json"))

def past_event(event_id):
    #Here we check to see if the event is a past event or not.
    #Only if it is a past event will users be able to add a rating for it
    #TODO: Compare to the exact time as well. Currently only filters by date.
    event_detail = EventDetails.query.filter_by(id=event_id).first()
    logging.info(date.today())
    if event_detail.end_date < date.today():
        return True
    else:
        return False


def previous_rating(attendee_username, event_id):
    #This function returns 0 if no previous rating
    #Else, it returns the value of the previous rating (1-5)

    prev_rating = EventRating.query.filter_by(attendee_username=attendee_username, event_id=event_id).first()
    logging.info("Existing Rating: ", prev_rating)
    if prev_rating is None:
        return 0
    else:
        return prev_rating.rating


@events.route("/events/submit_rating/<int:event_id>", methods=["GET", "POST"])
def submit_rating(event_id):
    # Get the user's username (assuming they are logged in)
    attendee_username = current_user.get_id()
    event_id = request.form.get('event_id')
    rating = request.form.get('rating')

    if event_id and rating and attendee_username: 
        # Check if the user has already rated this event, and update the rating if they have
        existing_rating = EventRating.query.filter_by(attendee_username=attendee_username, event_id=event_id).first()
        if existing_rating is not None:
            existing_rating.rating = rating
            flash('Rating Updated successfully', 'success')
        else:
            # Create a new rating record
            new_rating = EventRating(attendee_username=attendee_username ,event_id=event_id, rating=rating)
            db.session.add(new_rating)
            
            db.session.commit()

            flash('Rating submitted successfully', 'success')
    else:
        flash('Failed to submit rating. Please try again.', 'error')
        
    return redirect(url_for('events.show_event', id=event_id))


def create_google_calendar_event(id):
    # Get the event details from the database
    event = EventDetails.query.filter_by(id=id).all()

    if not event:
        print("Error! The event id passed to create_google_calendar_event() does not exit in the database")

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Google_Calendar/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        event_data = {
            "summary": event.name,
            "location": event.venue,
            "colorId": 6,
            "start": {
                "dateTime": f"{event.start_date}T{event.start_time}:00",
                "timeZone": "Canada/Eastern"
            },
            "end": {
                "dateTime": f"{event.end_date}T{event.end_time}:00",
                "timeZone": "Canada/Eastern"
            }
        }

        event = service.events().insert(calendarId="primary", body=event_data).execute()
        print(f'Event created: {event.get("htmlLink")}')

    except HttpError as error:
        print("An error occurred:", error)
