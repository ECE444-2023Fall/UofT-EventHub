from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    flash,
    current_app,
    request,
    redirect,
    url_for,
)
from flask_login import login_required, current_user
from sqlalchemy import delete
import logging

from app.main import db
from app.globals import Role
from app.auth import login_required
from app.database import Credentials, EventRegistration, EventDetails

events = Blueprint("events", __name__)

@events.route("/events/<int:id>", methods=["GET"])
@login_required
def show_event(id):
    print(f"Loading webpage for event ID: {id}")

    ## Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        print(
            "Integrity Error: The event ID passed to show_event has no valid entry in the database"
        )

    # Check if the user registered for the event
    is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id()).first()

    if is_registered is not None:
        flash("You are already registered for the event!", category="info")
        return render_template("event.html", event=event.__dict__, is_registered=True)
    else:
        return render_template("event.html", event=event.__dict__, is_registered=False)


@events.route("/events/send_file/<filename>")
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
    """
    # Check for valid event ID
    if event_id is None:
        logging.info("Cannot register user with an event ID: None")
        return ("1")

    logging.info("EVENT ID: %s", event_id)
    logging.info("USERNAME: %s", current_user.get_id())

    # Check for valid username
    user = Credentials.query.filter_by(username=current_user.get_id()).first()
    if not user:
        logging.warning("Cannot register user with an invalid username")
        return ("2")

    # We should also check if a username corresponds to a user and not an organizer
    if user.role != Role.USER.value:
        logging.warning("Cannot register an organizer")
        return ("3")

    #TODO: Check if event has enough seats left

    # Check if the user is already registered
    is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id()).first()
    if is_registered:
        logging.info("Cancelling user's registration")

        # Delete the registeration
        EventRegistration.query.filter_by(attendee_username=current_user.get_id(), event_id=event_id).delete()
        db.session.commit()

        flash("Cancelled registeration for the event!", category="success")
        event = EventDetails.query.filter_by(id=event_id).first()
        for key, val in event.__dict__.items():
            logging.info("Key: %s", key)
            logging.info("Value: %s", val)
        return render_template("event.html", event=event.__dict__, is_registered=False)

    # Register the user
    new_registration = EventRegistration(
        attendee_username=current_user.get_id(),
        event_id=event_id,
    )

    db.session.add(new_registration)
    db.session.commit()

    # Re-render the page showing user that registration is complete
    flash("Registered for the event!", category="success")
    event = EventDetails.query.filter_by(id=event_id).first()
    for key, val in event.__dict__.items():
        logging.info("Key: %s", key)
        logging.info("Value: %s", val)
    return render_template("event.html", event=event.__dict__, is_registered=True)
    
