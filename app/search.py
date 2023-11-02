from flask import Blueprint, render_template, request
from auth import login_required
from main import es

from database import EventDetails

search = Blueprint('search', __name__)

@search.route('/search', methods=['GET'])
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

