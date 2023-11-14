from flask import Flask, render_template, flash
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
import os, time
import logging, sys
from opensearchpy import OpenSearch

## Initialize and import databases schemas
db = SQLAlchemy()
from app.database import Credentials, EventDetails

# Initialize logger module
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#We migrated to opensearch as there is a AWS service available for it
#There is also not a big difference in usage from opensearch to ES because OS is just an extension of ES
es = OpenSearch(
        hosts=['REPLACE_WITH_ENDPOINT:443'],
        http_auth=('username', 'password')
    )

## Initialize elastic search server for autocomplete functionality
from app.globals import DB_NAME

def create_app(debug):
    app = Flask(__name__)
    app.debug = debug
    app.config["SECRET_KEY"] = "4829jfnwurduh4293k"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["GRAPHIC_DIRECTORY"] = path = os.path.join(
        app.root_path, "static", "event-assets"
    )
    db.init_app(app)
    bootstrap = Bootstrap(app=app)

    ## Make the app CORS compliant
    CORS(app)

    ## Register the paths so that we can use the routes defined there. E.g. Login and Register
    from app.auth import auth
    from app.user import user
    from app.organizer import organizer
    from app.events import events
    from app.search import search
    from app.filter import filter
    from app.user_events import user_events
    from app.account import account

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(user, url_prefix="/")
    app.register_blueprint(organizer, url_prefix="/")
    app.register_blueprint(events, url_prefix="/")
    app.register_blueprint(search, url_prefix="/")
    app.register_blueprint(filter, url_prefix="/")

    app.register_blueprint(user_events, url_prefix="/")
    app.register_blueprint(account, url_prefix="/")

    with app.app_context():
        db.create_all()

        # Index the events database using elasticsearch
        # Scrape any existing "junk" data
        if es.indices.exists(index="events"):
            es.options(ignore_status=[400, 404]).indices.delete(index="events")
        # Initialize the events index to an empty dict
        if not es.indices.exists(index="events"):
            es.index(index="events", body={})

        events_data = EventDetails.query.all()
        for row in events_data:
            event_detail = {
                "id": str(getattr(row, "id")),
                "name": str(getattr(row, "name")),
                "description": str(getattr(row, "short_description")),
                "category": str(getattr(row, "category")),
                "venue": str(getattr(row, "venue")),
                "additional_info": str(getattr(row, "additional_info")),
            }
            logging.info("The event dict for indexing:", event_detail)
            es.index(index="events", body=event_detail)

        es.indices.refresh(index="events")
        logging.info(es.cat.count(index="events", format="json"))

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(username):
        return Credentials.query.get(username)

    # Custom Error Handling for 404 Error
    @app.errorhandler(404)
    def page_not_found(error):
        logging.error(error)
        description = getattr(error, 'description')
        if "message" in description:
            flash(description["message"], category="danger")

        return render_template('error.html', error_code=404, error_msg="PAGE NOT FOUND"), 404

    @app.errorhandler(401)
    def unauthorized(error):
        logging.error(error)
        description = getattr(error, 'description')
        if "message" in description:
            flash(description["message"], category="danger")

        return render_template('error.html', error_code=401, error_msg="UNAUTHORIZED"), 401

    @app.errorhandler(500)
    def internal_server_error(error):
        logging.error(error)
        description = "Our team is working to fix the issue. Please try again later."
        flash(description, category="info")

        return render_template('error.html', error_code=500, error_msg="Oops! Something went wrong"), 500

    return app

app = create_app(debug=True)