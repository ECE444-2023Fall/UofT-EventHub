from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from forms import EventCreateForm

from main import db
from database import EventDetails, OrganizerEventDetails

events = Blueprint('events', __name__)

@events.route('/events/<int:id>', methods=['GET'])
@login_required
def show_event(id):
    print(f"This is the webpage for event ID: {id}")
    return render_template('event.html', event_id=id)