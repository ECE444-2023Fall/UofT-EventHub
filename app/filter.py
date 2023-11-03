from flask import Blueprint, render_template, request, redirect, url_for

from app.auth import login_required

filter = Blueprint("filter", __name__)

@filter.route("/filter_events", methods=["POST"])
@filter.route("/filter_events/<search>", methods=["POST"])
@login_required
def filter_events(search=None):
    if request.method != "POST":
        return
    
    print("User filtering for:", request.form["filter-tag"])
    tag = request.form["filter-tag"]

    if search == None:
        return redirect(url_for("user.main", filter=tag))
    return redirect(url_for("user.main", filter=tag, search=search))

def func_filter_events(events, tag):
    if tag == "all":
        return events
    
    filtered_events = {}
    for event_id in events.keys():
        if tag in events[event_id]["tags"]:
            filter_events[event_id] = events[event_id]
    return filtered_events
