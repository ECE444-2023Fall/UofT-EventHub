## This file contains functions for user's to register in a particular event

from flask import Blueprint, render_template, request, redirect, url_for
import logging

from app.auth import login_required

register = Blueprint("register", __name__)

@register.route("/event_register/<event_id>/<username>", methods=["GET", "POST"])
# @login_required
def register_user(event_id = None, username = None):
    """
    Returns:
    0: On successful registration
    1: If the event ID is invalid
    2: If the username is invalid
    """
    # Check for valid username and event ID
    if event_id is None:
        logging.info("Cannot register user with an event ID: None")
        return ("1")

    print(event_id)
    
    if username is None:
        logging.info("Cannot register user with an username: None")
        return ("2")

    return ("0")

    # We should also check if a username corresponds to a user and not an organizer

    # Check if event has enough seats left

    # Register the user and update the 

    
