import pytest
from pathlib import Path
from unittest.mock import MagicMock
from flask_login import current_user
from datetime import time, datetime
from app.main import app, db
from app.user import get_active_organizers
from app.database import EventDetails, Tag
from app.globals import Role

TEST_DB = "test3.db"

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


def user_register(client, num_string):
    # Register a new user
    response = client.post(
        "/register",
        data=dict(
            name="John Doe", username="my_event"+num_string, password1="password", password2="password", role=Role.USER.value
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(
        "/account/add",
        data=dict(
            firstname="John",
            lastname="Doe",
            year="4",
            course_type="Undergraduate",
            department="Music",
            campus="Scarborough",
            email="my_event@gmail.com"
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Logout of the system
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

def user_login(client, num_string):
    # Login back into the system
    response = client.post(
        "/", data=dict(username="my_event"+num_string, password="password"), follow_redirects=True
    )
    assert response.status_code == 200

def org_login(client, num_string):
    # Log in to the system
    response = client.post(
        "/", data=dict(username="Test_Org"+num_string, password="password"), follow_redirects=True
    )
    assert response.status_code == 200

def logout(client):
    # Logout of the system
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

def org_register(client, num_string):
    test_organizer_data = {
        "name": "Test Organizer",
        "username": "Test_Org"+num_string,
        "password1": "password",
        "password2": "password",
        "role": Role.ORGANIZER.value,
    }
    # Testing access to event register page as an organizer
    response = client.post("/register", data=test_organizer_data, follow_redirects=True)
    assert response.status_code == 200
    # Logout
    logout(client)

def create_test_event(client, num_string):
    # Create a basic event
    #this tests event creation as well
    new_event = EventDetails(
        name="my_test_event"+num_string,
        short_description="This is my test event number: "+num_string,
        category="Academic",
        start_date=datetime(2024, 11, 15).date(),
        end_date=datetime(2024, 11, 15).date(),
        image="placeholder.png",
        start_time=time(9, 0, 0),
        end_time=time(10, 0, 0),
        max_capacity="5"
    )
    db.session.add(new_event)
    db.session.commit()
    
    events = EventDetails.query.all()
    assert len(events) == int(num_string)
    
    #check if event admin page can be accessed
    response = client.get("/events/admin/"+num_string, follow_redirects=True)
    assert response.status_code == 200
    
def create_past_event(client, num_string):
    # Create a past event
    new_event = EventDetails(
        name="my_test_event"+num_string,
        short_description="This is my test event number: "+num_string,
        category="Academic",
        start_date=datetime(2023, 10, 15).date(),
        end_date=datetime(2023, 10, 15).date(),
        image="placeholder.png",
        start_time=time(9, 0, 0),
        end_time=time(10, 0, 0),
        max_capacity="5"
    )
    db.session.add(new_event)
    db.session.commit()
    
    events = EventDetails.query.all()
    assert len(events) == int(num_string)
    
    #check if event admin page can be accessed
    response = client.get("/events/admin/"+num_string, follow_redirects=True)
    assert response.status_code == 200

def user_event_registration(client, num_string):
    # tests event registration for users
    response = client.post("/events/register/"+num_string, follow_redirects=True)
    assert response.status_code == 200

def test_rate_upcoming_event(client):
    # test if users can rate for events that are not past events (should not work)
    num_string = "1"
    # First register organizer1
    org_register(client, num_string)
    # organizer1 logs in
    org_login(client, num_string)
    # organizer1 creates event1 
    create_test_event(client, num_string)
    # organizer1 logs out
    logout(client)
    # register user1
    user_register(client, num_string)
    # user1 logs in
    user_login(client, num_string)
    # user1 registers for event
    user_event_registration(client, num_string)
    # user1 tries to submit rating for an upcoming event
    response = client.post("/events/submit_rating/"+num_string, follow_redirects=True)
    assert response.status_code == 401
    logout(client)

def test_past_event_registration(client):
    # test if users can register for past events (Should not work)
    num_string = "2"
    # First register organizer1
    org_register(client, num_string)
    # organizer2 logs in
    org_login(client, num_string)
    # organizer2 creates event1 
    create_past_event(client, num_string)
    # organizer2 logs out
    logout(client)
    # register user2
    user_register(client, num_string)
    # user2 logs in
    user_login(client, num_string)
    # user2 attepts to register for event
    response = client.post("/events/register/"+num_string, follow_redirects=True)
    assert response.status_code == 401
    logout(client)

def test_calendar_invite(client):
    # organizer logs in, creates an event and logs out
    org_login(client, "1")
    create_test_event(client, "3")
    logout(client)

    # user logs in
    user_login(client, "1")
    # user tries to view calendar invite for an event that does not exist, so fails
    response = client.get("/events/"+ "1000" + "/calendar_invite", follow_redirects=True)
    assert response.status_code == 404

    # user tries to view calendar invite for an event that they have not registered for, so fails
    response = client.get("/events/"+ "3" + "/calendar_invite", follow_redirects=True)
    assert response.status_code == 404
    
    # user registers for event and can view calendar invite, so passes
    user_event_registration(client, "3")
    response = client.get("/events/"+ "3" + "/calendar_invite", follow_redirects=True)
    assert response.status_code == 200
    logout(client)
