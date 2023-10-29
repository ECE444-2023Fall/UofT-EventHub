import pytest
from app.main import app, db
from pathlib import Path

TEST_DB = "test.db"

# Test function written by Rahul
@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
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
