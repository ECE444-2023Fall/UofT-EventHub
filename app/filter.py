from flask import Blueprint, request, redirect, url_for
from datetime import date, datetime
import logging

from app.auth import login_required

filter = Blueprint("filter", __name__)

@filter.route("/filter_events", methods=["POST"])
@filter.route("/filter_events/<search>", methods=["POST"])
@login_required
def filter_events(search=None):
    if request.method != "POST":
        return
    
    logging.info("The calling page is: %s", request.referrer)

    logging.info("User filtering for: %s", request.form["filter-tag"])
    tag = request.form["filter-tag"]

    # Assemble the arguments for the redrect link based on 
    # the filter tag selected
    redirect_args = {}
    if tag != "clear":
        # Add the filter tag value provided "Clear Filters" was not selected
        redirect_args["filter"] = tag
    if search != None:
        # Pass on the existing search value
        redirect_args["search"] = search
        if tag == "clear":
            # Add this filter tag to follow the route layout of user.main
            redirect_args["filter"] = "all"

    #If the caller is the my events page then it should redirect there
    if (request.referrer.find("/myevents/") != -1):
        return redirect(url_for("user_events.main", **redirect_args))
    else:
        return redirect(url_for("user.main", **redirect_args))

def filter_for_today_events(events):
    return { 
        event_id: events[event_id] 
        for event_id in events.keys() 
        if events[event_id]["start_date"] == date.today().strftime('%Y-%m-%d')
    }

def filter_for_inperson_events(events):
    return { 
        event_id: events[event_id] 
        for event_id in events.keys() 
        if not int(events[event_id]["is_online"])
    }

def filter_for_free_events(events):
    return { 
        event_id: events[event_id] 
        for event_id in events.keys() 
        if float(events[event_id]["ticket_price"]) == 0.0
    }

def filter_events_on_category(events, category):
    return {
        event_id: events[event_id] 
        for event_id in events.keys() 
        if (events[event_id]["category"] == category)
    }

def filter_events_on_event_ids_list(events, event_ids):
    # Loop through event_ids: If event_id is in events, then return that event
    return {
        event_id: events[event_id] 
        for event_id in event_ids 
        if event_id in events
    }

def filter_for_past_events(events):
    # Return events that are past events
    return { 
        event_id: events[event_id] 
        for event_id in events.keys() 
        if (events[event_id]["start_date"] < date.today().strftime('%Y-%m-%d')) or (events[event_id]["start_date"] == date.today().strftime('%Y-%m-%d') and events[event_id]["start_time"] < datetime.now().strftime("%H:%M:%S"))
    }