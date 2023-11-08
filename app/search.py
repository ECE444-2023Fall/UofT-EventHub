from flask import Blueprint, render_template, request, redirect, url_for
import logging

from app.main import es
from app.auth import login_required

search = Blueprint("search", __name__)


@search.route("/search", methods=["GET"])
def search_autocomplete():
    # This function is a standalone method to query our events database with a set of keywords
    # Login won't be required for this method
    
    query = request.args["search"].lower()
    tokens = query.split(" ")

    logging.info("Search autocomplete received the query: ", tokens)

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


@search.route("/search_events/<filter>", methods=["POST"])
@login_required
def search_events(filter="all"):
    if request.method != "POST":
        return

    # Assemble the arguments for the redrect link based on 
    # if the user decided to "Clear Search" or "Search"
    
    # Pass on the existing filter value
    redirect_args = {"filter": filter}
    if "clear-search-button" in request.form.keys():
        # Omit the search query from the redirect link
        if filter == "all":
            # If there is no search query and filter = "all"
            # then it is redundant to pass a filter argument
            del redirect_args["filter"]
    else:
        # Add the search query in the redirect link
        logging.info("User searched for: %s", request.form["query"])
        query = request.form["query"]
        redirect_args["search"] = query

    #If the caller is the my events page then it should redirect there
    if (request.referrer.find("/myevents/") != -1):
        return redirect(url_for("user_events.main", **redirect_args))
    else:
        return redirect(url_for("user.main", **redirect_args))

# Primary ElasticSearch retrival logic
# Gets the events depending on the search query
def get_eventids_matching_search_query(query):
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
    list_event_ids = []
    for result in resp["hits"]["hits"]:
        list_event_ids.append( int(result["_source"]["id"]) )

    return list_event_ids
