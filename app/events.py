from flask import (
    Blueprint,
    render_template,
    send_from_directory,
)
from flask_login import login_required
from flask import current_app

import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.database import EventDetails

events = Blueprint("events", __name__)

@events.route("/events/<int:id>", methods=["GET"])
@login_required
def show_event(id):
    print(f"Loading webpage for event ID: {id}")

    # Get all the details for the event
    event = EventDetails.query.filter_by(id=id).first()

    if not event:
        print(
            "Integrity Error: The event ID passed to show_event has no valid entry in the database"
        )

    return render_template("event.html", event=event.__dict__)


@events.route("/events/send_file/<filename>")
@login_required
def send_file(filename):
    """
    This function is used to fetch event banner images for event.html pages"
    """

    return send_from_directory(current_app.config["GRAPHIC_DIRECTORY"], filename)


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