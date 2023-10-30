import pytest
from app.main import app, db
from pathlib import Path
from flask_login import current_user

TEST_DB = "test.db"

# Test function written by Rahul
@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config['WTF_CSRF_ENABLED'] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

# Test function written by Rahul
# Test if home page is accessible
def test_index():
    tester = app.test_client()
    response = tester.get("/", content_type="html/text")
    assert response.status_code == 200


# Test function written by Rahul
# Test if a new user can successfully register
def test_register_success(client):
    response = client.post("/register", data=dict(username="user123",
        password1="PaSsWoRd",
        password2="PaSsWoRd",
        role="user"),
        follow_redirects=True)
    assert response.status_code == 200
    assert b"Account created!" in response.data


# Test function written by Hetav
# Test if a registered user is able to login
def test_user_login_success(client):
    # Register a new user
    response = client.post("/register", data=dict(username="admin",
        password1="password",
        password2="password",
        role="user"),
        follow_redirects=True)
    assert response.status_code == 200

    # Logout of the system
    response = client.get("/logout",
        follow_redirects=True)
    assert response.status_code == 200

    # Login back into the system
    response = client.post("/", data=dict(username="admin",
        password="password"),
        follow_redirects=True)
    assert response.status_code == 200

    # The system should redirect the user to the event feed
    assert b"All Events List" in response.data


# Test function written by Kshitij
# Test if a registered organizer is able to login
def test_organizer_login_success(client):
    # Register a new user
    response = client.post("/register", data=dict(username="admin2",
        password1="password2",
        password2="password2",
        role="organizer"),
        follow_redirects=True)
    assert response.status_code == 200

    # Logout of the system
    response = client.get("/logout",
        follow_redirects=True)
    assert response.status_code == 200

    # Login back into the system
    response = client.post("/", data=dict(username="admin2",
        password="password2"),
        follow_redirects=True)
    assert response.status_code == 200

    # The system should redirect the organizer to the main organizer page
    assert b"MAIN ORGANIZER PAGE" in response.data


# Test function written by Fabin
# Test if a user can access organizer pages without proper login
def test_organizer_content_auth(client):
    # Testing access without logining in
    response = client.get("/organizer", content_type="html/text")
    assert response.status_code == 401

    test_organizer_data = {
        'username': "admin",
        'password1': "password",
        'password2': "password",
        'role': "organizer"
    }
    test_user_data = {
        'username': "user1",
        'password1': "password",
        'password2': "password",
        'role': "user"
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