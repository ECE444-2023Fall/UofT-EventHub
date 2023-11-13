import pytest
from pathlib import Path
from unittest.mock import MagicMock
from flask_login import current_user
from app.main import app, db
from app.user import get_active_organizers
from app.database import EventDetails, Tag
from app.globals import Role

TEST_DB = "test2.db"

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
            name="Jane Doe", username="my_account"+num_string, password1="password", password2="password", role=Role.USER.value
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(
        "/account/add",
        data=dict(
            firstname="Jane",
            lastname="Doe",
            year="4",
            course_type="Undergraduate",
            department="Law",
            campus="Scarborough",
            email="my_account@gmail.com"
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
        "/", data=dict(username="my_account"+num_string, password="password"), follow_redirects=True
    )
    assert response.status_code == 200

def user_logout(client):
    # Logout of the system
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

def test_my_account_access_user(client):
    # register first user
    user_register(client, "1")
    #access my account page as user1
    user_login(client, "1")
    
    response = client.get("/account/show", content_type="html/text")
    assert response.status_code == 200
    # Logout
    user_logout(client)


def test_update_my_account_info(client):
     # register second user
    user_register(client, "2")
    #access my account page as user2
    user_login(client, "2")
    
    response = client.post(
        "/account/show",
        data=dict(
            firstname="Jane",
            lastname="Doe",
            year="3",
            course_type="Undergraduate",
            department="Music",
            campus="Scarborough",
            email="my_account@gmail.com"
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Logout
    user_logout(client)
    