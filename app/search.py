from flask import Blueprint, render_template, request, redirect, url_for

from app.main import es
from app.auth import login_required

search = Blueprint("search", __name__)


@search.route("/search", methods=["GET"])
@login_required
def search_autocomplete():
    query = request.args["search"].lower()
    tokens = query.split(" ")

    clauses = [
        {
            "span_multi": {
                "match": {"fuzzy": {"name": {"value": i, "fuzziness": "AUTO"}}}
            }
        }
        for i in tokens
    ]

    payload = {
        "bool": {
            "must": [{"span_near": {"clauses": clauses, "slop": 0, "in_order": False}}]
        }
    }

    resp = es.search(index="events", query=payload, size=10)

    # Return a list of event name and id ordered by the most relevant on top
    return [
        [result["_source"]["name"], result["_source"]["id"]]
        for result in resp["hits"]["hits"]
    ]


@search.route("/search_events", methods=["POST"])
@search.route("/search_events/<filter>", methods=["POST"])
@login_required
def search_events(filter="all"):
    if request.method != "POST":
        return

    print("User searched for:", request.form["query"])
    query = request.form["query"]

    return redirect(url_for("user.main", search=query, filter=filter))

# This Function contains the logic that searches for the events based
# on the input search_query
def func_search_events(query):
    tokens = query.split(" ")

    # Make a JSON query to elastic search to get the list of relevant events
    clauses = [
        {
            "span_multi": {
                "match": {"fuzzy": {"name": {"value": i, "fuzziness": "AUTO"}}}
            }
        }
        for i in tokens
    ]

    payload = {
        "bool": {
            "must": [{"span_near": {"clauses": clauses, "slop": 0, "in_order": False}}]
        }
    }

    resp = es.search(index="events", query=payload, size=10)

    ## Make a dict for relevant event details
    dict_of_events_details = {}
    for result in resp["hits"]["hits"]:
        event_detail = {}

        for column in result["_source"].keys():
            event_detail[column] = result["_source"][column]

        dict_of_events_details[result["_source"]["id"]] = event_detail

    print("The relevant event list is:", dict_of_events_details)
    return dict_of_events_details
