from flask import Blueprint, render_template, request
from auth import login_required
from main import es

from database import EventDetails

search = Blueprint('search', __name__)

@search.route('/search', methods=['GET'])
def search_autocomplete():
    query = request.args["search"].lower()
    print("User searched for:", query)
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
    return [result['_source']['name'] for result in resp['hits']['hits']]

