from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from forms import EventCreateForm

from main import db
from database import EventDetails

events = Blueprint('events', __name__)

@events.route('/events/<int:id>', methods=['GET'])
@login_required
def show_event(id):
    print(f"Loading webpage for event ID: {id}")

    ## Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        print("Integrity Error: The event ID passed to show_event has no valid entry in the database")

    return render_template('event.html', event=event.__dict__)