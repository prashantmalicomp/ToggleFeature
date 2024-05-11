import os
import pytest
from app import create_app
from app.models import db, FeatureToggle, User, ToggleStateEnum


@pytest.fixture
def app():
    os.environ['FLASK_ENV'] = "testing"
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# Sample test cases for GET /toggles
def test_get_toggles(client):
    response = client.get("/api/v1/toggles")
    assert response.status_code == 200
    assert len(response.json) == 0  # Assuming there are no toggles initially


def test_create_user(client):
    # create prerequisite user data
    user_data = {
        "username": "testuser",
        "password": "Test@123",
        "role": "ADMIN",
        "email": "testuser123@gmail.com"
    }

    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201
    data = response.json
    user_id = data['id']
    user = User.query.get(user_id)
    assert user is not None
    assert user.id == 1
    # validate role & username & email
    assert user.username == data['username'] == user_data['username']
    assert user.role == data['role'] == user_data['role']
    assert user.email == data['email'] == user_data['email']


def test_get_user_detail_by_user_id(client):
    test_create_user(client)
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
    data = response.json
    user_id = data['id']
    user = User.query.get(user_id)
    assert user is not None
    assert user.id == 1
    # validate role & username & email
    assert user.username == data['username']
    assert user.role == data['role']
    assert user.email == data['email']


def test_get_user_detail_by__invalid_user_id(client):
    response = client.get("/api/v1/users/11")
    assert response.status_code == 404
    assert response.json['error'] == 'User not found'


def test_create_user_with_invalid_role(client):
    # create prerequisite user data
    user_data = {
        "username": "testuser",
        "password": "Test@123",
        "role": "Test",
        "email": "testuser123@gmail.com"
    }

    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 400
    data = response.json
    assert data['error'] == "Invalid role : Role should be in 'ADMIN' or 'MEMBER'"


# Sample test cases for POST /toggles/env/user_id
def test_create_toggle(client):
    test_create_user(client)
    data = {
        "identifier": "Toggle 4",
        "description": "This toggle user for Dev environment",
        "state": 1,
        "environment": "DEV",
        "notes": "This is simple note for dev",
        "created_by": 1
    }
    response = client.post("/api/v1/toggles/DEV/1", json=data)
    assert response.status_code == 201
    toggle_id = response.json["id"]
    response_data = response.json
    # Retrieve the toggle and verify it exists
    toggle = FeatureToggle.query.get(toggle_id)
    assert toggle is not None

    # validate toggle environment, identifier, description & notes, created_by
    assert response_data['identifier'] == data['identifier']
    assert response_data['environment'] == data['environment']
    assert response_data['notes'] == data['notes']
    assert response_data['created_by'] == data['created_by']
    assert response_data['state'] == data['state']
    assert response_data['sb_id']
    assert response_data['toggle_state'] == ToggleStateEnum.ENABLE.name

# Sample test cases for POST /toggles/env/user_id
def test_create_duplicate_toggle_with_same_identifier(client):
    test_create_toggle(client)
    data = {
        "identifier": "Toggle 4",
        "description": "This toggle user for Dev environment",
        "state": 1,
        "environment": "DEV",
        "notes": "This is simple note for dev",
        "created_by": 1
    }
    response = client.post("/api/v1/toggles/DEV/1", json=data)
    assert response.status_code == 404
    assert response.json['error'] == f'Toggle - Toggle 4 already exists'


# Sample test cases for PUT /toggles/toggle_id
def test_update_toggle(client):
    # create toggle with Enabled state = 1
    test_create_toggle(client)

    # Assuming toggle exists with ID 1
    data = {
        "state": 0
    }

    # Disable toggle state = 0
    response = client.put("/api/v1/toggles/1?env=DEV&user_id=1", json=data)

    assert response.status_code == 200
    # Verify the toggle is updated
    toggle = FeatureToggle.query.filter(FeatureToggle.sb_id == 1,
                                        FeatureToggle.status == 'ACTIVE').first()
    assert toggle is not None

    # Validate toggle updates fields & versioning mechanism
    assert toggle.version == 2
    assert toggle.state == 0
    assert toggle.sb_id == 1
    assert toggle.status == 'ACTIVE'

    # check previous version 1 will be superseded or not
    prev_toggle = FeatureToggle.query.filter(FeatureToggle.sb_id == 1,
                                             FeatureToggle.status == 'SUPERSEDED').first()
    assert prev_toggle is not None
    assert prev_toggle.version == 1
    assert prev_toggle.state == 1
    assert prev_toggle.sb_id == 1
    assert prev_toggle.status == 'SUPERSEDED'

