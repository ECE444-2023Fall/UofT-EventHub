import pytest
from pathlib import Path
from unittest.mock import MagicMock
from flask_login import current_user
from app.main import app, db
from app.user import get_active_organizers
from app.database import EventDetails, Tag
from app.events import create_google_calendar_event

TEST_DB = "test.db"


# Test function written by Rahul
@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        # Commenting out right now as all .db instances get deleted. This makes testing easier as we retain all created database info
        #db.drop_all()


# Test function written by Rahul
# Test if home page is accessible
def test_index():
    tester = app.test_client()
    response = tester.get("/", content_type="html/text")
    assert response.status_code == 200


# Test function written by Rahul
# Test if a new user can successfully register
def test_register_success(client):
    response = client.post(
        "/register",
        data=dict(
            username="user123", password1="PaSsWoRd", password2="PaSsWoRd", role="user"
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account created!" in response.data


# Test function written by Hetav
# Test if a registered user is able to login
def test_user_login_success(client):
    # Register a new user
    response = client.post(
        "/register",
        data=dict(
            username="admin", password1="password", password2="password", role="user"
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Logout of the system
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

    # Login back into the system
    response = client.post(
        "/", data=dict(username="admin", password="password"), follow_redirects=True
    )
    assert response.status_code == 200

    # The system should redirect the user to the event feed
    assert b"All Events List" in response.data


# Test function written by Kshitij
# Test if a registered organizer is able to login
def test_organizer_login_success(client):
    # Register a new user
    response = client.post(
        "/register",
        data=dict(
            username="admin2",
            password1="password2",
            password2="password2",
            role="organizer",
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Logout of the system
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

    # Login back into the system
    response = client.post(
        "/", data=dict(username="admin2", password="password2"), follow_redirects=True
    )
    assert response.status_code == 200

    # The system should redirect the organizer to the main organizer page
    assert b"MAIN ORGANIZER PAGE" in response.data


def test_unathorized_logout():
    tester = app.test_client()
    response = tester.get("/logout", content_type="html/text")
    assert response.status_code == 401


# Test function written by Fabin
# Test if a user can access organizer pages without proper login
def test_organizer_content_auth(client):
    # Testing access without logining in
    response = client.get("/organizer", content_type="html/text")
    assert response.status_code == 401

    test_organizer_data = {
        "username": "admin",
        "password1": "password",
        "password2": "password",
        "role": "organizer",
    }
    test_user_data = {
        "username": "user1",
        "password1": "password",
        "password2": "password",
        "role": "user",
    }

    # Testing access to organizer page as a user
    response = client.post("/register", data=test_user_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.get("/organizer", content_type="html/text")
    assert response.status_code == 401

    response = client.get("/logout")

    # Testing access to organizer page as a organizer
    response = client.post("/register", data=test_organizer_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.get("/organizer", content_type="html/text")
    assert response.status_code == 200


# Test function written by Jhanavi
# Test if a organizer can access the user pages without proper login
def test_user_content_auth(client):
    # Testing access without logining in
    response = client.get("/user", content_type="html/text")
    assert response.status_code == 401

    test_organizer_data = {
        "username": "jhanavi_org",
        "password1": "test_password",
        "password2": "test_password",
        "role": "organizer",
    }
    test_user_data = {
        "username": "jhanavi_user",
        "password1": "test_password",
        "password2": "test_password",
        "role": "user",
    }

    # Testing access to user page as a organizer
    response = client.post("/register", data=test_organizer_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.get("/user", content_type="html/text")
    assert response.status_code == 401

    response = client.get("/logout")
    # Testing access to user page as a user
    response = client.post("/register", data=test_user_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.get("/user", content_type="html/text")
    assert response.status_code == 200


# Test function written by Jhanavi
def test_organiser_add_events_endpoint(client):
    test_organizer_data = {
        "username": "jhanavi2",
        "password1": "password",
        "password2": "password",
        "role": "organizer",
    }
    # Testing access to event register page as an organizer
    response = client.post("/register", data=test_organizer_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.get("/organizer/create_event", content_type="html/text")
    assert response.status_code == 200


def test_create_event_with_tags(client):
    # Create tags
    social_tag = Tag(name='social')
    cultural_tag = Tag(name='cultural')
    networking_tag = Tag(name='networking')

    # Create an event and associate tags
    new_event = EventDetails(name="Sample Event", description="A test event", venue="Sample Venue")
    new_event.tags.extend([social_tag, cultural_tag, networking_tag])

    db.session.add(new_event)
    db.session.commit()

    # Query events with their associated tags
    events = EventDetails.query.all()
    assert len(events) == 1
    event = events[0]
    assert event.name == "Sample Event"
    assert len(event.tags) == 3
    assert {"social", "cultural", "networking"} == {tag.name for tag in event.tags}


# Mocking the necessary objects for testing
class MockEvent:
    id = 1
    name = "Test Event"
    venue = "Test Venue"
    start_date = "2023-12-25"
    start_time = "09:00"
    end_date = "2023-12-25"
    end_time = "11:00"

def test_create_google_calendar_event(client, monkeypatch):
    # Mocking the EventDetails.query.get method to return the mock event created above
    monkeypatch.setattr(EventDetails.query, 'get', MagicMock(return_value=MockEvent))

    # Calling the function with the event id == 1
    result = create_google_calendar_event(1)

    assert "Event created:" in result


def test_get_distinct_organizers(client):
    organizer_usernames = get_active_organizers()
    assert isinstance(organizer_usernames, list)
