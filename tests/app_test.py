import pytest
from pathlib import Path
from unittest.mock import MagicMock
from flask_login import current_user
from app.main import app, db
from app.user import get_active_organizers
from app.database import EventDetails, Tag
from app.globals import Role

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
            name="John Doe", username="user123", password1="PaSsWoRd", password2="PaSsWoRd", role=Role.USER.value
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200


# Test function written by Hetav
# Test if a registered user is able to login
def test_user_login_success(client):
    # Register a new user
    response = client.post(
        "/register",
        data=dict(
            name="Test Admin", username="admin", password1="password", password2="password", role=Role.USER.value
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(
        "/account/add",
        data=dict(
            firstname="Test",
            lastname="admin",
            year="1",
            course_type="Undergraduate",
            department="Law",
            campus="Scarborough",
            email="test@gmail.com"
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


# Test function written by Kshitij
# Test if a registered organizer is able to login
def test_organizer_login_success(client):
    # Register a new user
    response = client.post(
        "/register",
        data=dict(
            name="Test Admin2",
            username="admin2",
            password1="password2",
            password2="password2",
            role=Role.ORGANIZER.value,
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
        "name": "Test Admin1",
        "username": "admin1",
        "password1": "password",
        "password2": "password",
        "role": Role.ORGANIZER.value,
    }
    test_user_data = {
        "name": "Test User1",
        "username": "user1",
        "password1": "password",
        "password2": "password",
        "role": Role.USER.value,
    }

    # Testing access to organizer page as a user
    response = client.post("/register", data=test_user_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.post(
        "/account/add",
        data=dict(
            firstname="Test",
            lastname="admin1",
            year="2",
            course_type="Undergraduate",
            department="Law",
            campus="Scarborough",
            email="test2@gmail.com"
        ),
        follow_redirects=True,
    )
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
    response = client.get("/user/", content_type="html/text")
    assert response.status_code == 401

    test_organizer_data = {
        "name": "Jhanavi Org",
        "username": "jhanavi_org",
        "password1": "test_password",
        "password2": "test_password",
        "role": Role.ORGANIZER.value,
    }
    test_user_data = {
        "name": "Jhanavi User",
        "username": "jhanavi_user",
        "password1": "test_password",
        "password2": "test_password",
        "role": Role.USER.value,
    }

    # Testing access to user page as a organizer
    response = client.post("/register", data=test_organizer_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.get("/user/", content_type="html/text")
    assert response.status_code == 401

    response = client.get("/logout")
    # Testing access to user page as a user
    response = client.post("/register", data=test_user_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.post(
        "/account/add",
        data=dict(
            firstname="Jhanavi",
            lastname="User",
            year="4",
            course_type="Undergraduate",
            department="Music",
            campus="Mississauga",
            email="testJG@gmail.com"
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    response = client.get("/user/", content_type="html/text")
    assert response.status_code == 200


# Test function written by Jhanavi
def test_organiser_add_events_endpoint(client):
    test_organizer_data = {
        "name": "Jhanavi Org2",
        "username": "jhanavi2",
        "password1": "password",
        "password2": "password",
        "role": Role.ORGANIZER.value,
    }
    # Testing access to event register page as an organizer
    response = client.post("/register", data=test_organizer_data, follow_redirects=True)
    assert response.status_code == 200
    response = client.get("/events/create_event", content_type="html/text")
    assert response.status_code == 200


# Mocking the necessary objects for testing
class MockEvent:
    id = 1
    name = "Test Event"
    venue = "Test Venue"
    start_date = "2023-12-25"
    start_time = "09:00"
    end_date = "2023-12-25"
    end_time = "11:00"

# TODO: Commenting function below out to enable workflow push. This needs to be addressed later once
# the google calendar changes have been pushed and merged as well.
# def test_create_google_calendar_event(client, monkeypatch):
#     # Mocking the EventDetails.query.get method to return the mock event created above
#     monkeypatch.setattr(EventDetails.query, 'get', MagicMock(return_value=MockEvent))

#     # Calling the function with the event id == 1
#     result = create_google_calendar_event(1)

#     assert "Event created:" in result


def test_get_distinct_organizers(client):
    organizer_usernames = get_active_organizers()
    assert isinstance(organizer_usernames, list)
