## This file contains functions for user's to register in a particular event

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
import logging

from app.main import db
from app.globals import Role
from app.auth import login_required
from app.database import Credentials, EventRegistration

register = Blueprint("register", __name__)

@register.route("/event_register/<event_id>", methods=["GET", "POST"])
@login_required
def register_user(event_id = None):
    """
    Description: Responsible for registering the user for an event

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

    logging.info("EVENT ID:", event_id)
    logging.info("USERNAME:", current_user.get_id())

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

    #TODO: Check if the user is already registered
    is_registered = EventRegistration.query.filter_by(attendee_username=current_user.get_id()).first()
    if is_registered:
        logging.warning("User is already registered")
        return ("4")

    # Register the user
    new_registration = EventRegistration(
        attendee_username=current_user.get_id(),
        event_id=event_id,
    )

    db.session.add(new_registration)
    db.session.commit()

    # Indicate that the user has registered
    flash("Registered for the event!", category="success")

    return ("0")

    
