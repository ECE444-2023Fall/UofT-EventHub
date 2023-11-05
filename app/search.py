from flask import Blueprint, render_template, request

from app.main import es
from app.auth import login_required
from app.database import EventDetails

search = Blueprint('search', __name__)

@search.route('/search', methods=['GET'])
def search_autocomplete():
    query = request.args["search"].lower()
    tokens = query.split(" ")

# This block creates a list of clauses, each specifying a fuzzy matching criterion for a token in the 'tokens' list.
# Each clause is configured to perform a fuzzy match on the 'name' field of the Elasticsearch documents.

    clauses = [
        {
            "span_multi": {
                "match": {"fuzzy": {"name": {"value": i, "fuzziness": "AUTO"}}}
            }
        }
        for i in tokens
    ]

    # Constructing the search query parameters.
    # This operation looks for proximity matches of the clauses with zero distance and not necessarily in order.

    payload = {
        "bool": {
            "must": [{"span_near": {"clauses": clauses, "slop": 0, "in_order": False}}]
        }
    }

    # It searches the 'events' index and retrieves a maximum of 10 matching results.
    resp = es.search(index="events", query=payload, size=10)

    # Return a list of event name and id ordered by the most relevant on top
    return [[result['_source']['name'], result['_source']['id']] for result in resp['hits']['hits']]

@search.route('/search_events', methods=['POST'])
def search_events():
    if request.method != 'POST':
        return
    
    print("User searched for:", request.form['query'])
    query = request.form['query']
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
    for result in resp['hits']['hits']:
        event_detail = {}

        for column in result['_source'].keys():
            event_detail[column] = result['_source'][column]

        dict_of_events_details[result['_source']['id']] = event_detail

    print("The relevant event list is:", dict_of_events_details)
    return render_template('user_main.html', event_data=dict_of_events_details)

