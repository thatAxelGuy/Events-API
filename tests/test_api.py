import requests


# Health
def test_health_returns_healthy(base_url):
    response = requests.get(f"{base_url}/api/health")

    assert response.status_code == 999
    assert response.json() == {"status": "healthy"}


# Auth
def test_register_user_creates_new_user(base_url, unique_username):
    url = f"{base_url}/api/auth/register"
    credentials = {"username": unique_username, "password": "securepassword123"}

    response = requests.post(url, json=credentials)
    assert response.status_code == 201

    data = response.json()
    assert data["message"] == "User created successfully"
    assert data["user"]["username"] == unique_username


def test_register_duplicate_username_returns_400(base_url, unique_username):
    credentials = {"username": unique_username, "password": "securepassword123"}

    first_register = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert first_register.status_code == 201

    second_register = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert second_register.status_code == 400
    data = second_register.json()
    assert data["error"] == "Username already exists"


def test_login_returns_jwt_token(base_url, unique_username):
    credentials = {"username": unique_username, "password": "securepassword123"}
    register_user = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert register_user.status_code == 201

    response = requests.post(f"{base_url}/api/auth/login", json=credentials)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["access_token"]


# Events
def test_create_public_event_requires_auth_and_succeeds_with_token(
    base_url, auth_token
):
    event = {
        "title": "Python Meetup",
        "description": "Monthly Python developer meetup",
        "date": "2026-12-15T18:00:00",
        "location": "Tech Hub, Room 101",
        "capacity": 50,
        "is_public": True,
        "requires_admin": False,
    }
    url = f"{base_url}/api/events"
    response = requests.post(
        url, json=event, headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == event["title"]
    assert data["location"] == event["location"]
    assert data["capacity"] == event["capacity"]


def test_create_event_without_token_returns_401(base_url):
    event = {
        "title": "Python Meetup",
        "description": "Monthly Python developer meetup",
        "date": "2026-12-15T18:00:00",
    }
    response = requests.post(f"{base_url}/api/events", json=event)
    assert response.status_code == 401
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"


def test_create_event_with_malformed_header_returns_422(base_url):
    event = {
        "title": "Python Meetup",
        "description": "Monthly Python developer meetup",
        "date": "2026-12-15T18:00:00",
    }
    response = requests.post(
        f"{base_url}/api/events", json=event, headers={"Authorization": "Bearer"}
    )
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert (
        data["msg"]
        == "Bad Authorization header. Expected 'Authorization: Bearer <JWT>'"
    )


def test_get_non_existent_event_returns_404(base_url):
    url = f"{base_url}/api/events/99999999"
    response = requests.get(url)
    assert response.status_code == 404


# RSVP
def test_rsvp_to_public_event_succeeds(base_url, auth_token):
    event = {
        "title": "Python Meetup",
        "description": "Monthly Python developer meetup",
        "date": "2026-12-15T18:00:00",
        "location": "Tech Hub, Room 101",
        "capacity": 50,
        "is_public": True,
        "requires_admin": False,
    }
    event_creation = requests.post(
        f"{base_url}/api/events",
        json=event,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert event_creation.status_code == 201
    event_id = event_creation.json()["id"]

    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}", json={"attending": True}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["event_id"] == event_id
    assert data["attending"] is True


def test_rsvp_to_private_event_without_token_returns_401(base_url, auth_token):
    event = {
        "title": "Python Meetup",
        "description": "Monthly Python developer meetup",
        "date": "2026-12-15T18:00:00",
        "location": "Tech Hub, Room 101",
        "capacity": 50,
        "is_public": False,
        "requires_admin": False,
    }
    event_creation = requests.post(
        f"{base_url}/api/events",
        json=event,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert event_creation.status_code == 201
    event_data = event_creation.json()
    event_id = event_data["id"]

    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}", json={"attending": True}
    )
    assert response.status_code == 401
    response_data = response.json()
    assert response_data["error"] == "Authentication required for this event"


def test_rsvp_again_updates_existing_rsvp(base_url, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    event = {"title": "Python Meetup", "date": "2026-12-15T18:00:00", "is_public": True}
    event_response = requests.post(
        f"{base_url}/api/events", json=event, headers=headers
    )
    assert event_response.status_code == 201
    event_id = event_response.json()["id"]
    rsvp_url = f"{base_url}/api/rsvps/event/{event_id}"

    first = requests.post(rsvp_url, json={"attending": True}, headers=headers)
    assert first.status_code == 201

    second = requests.post(rsvp_url, json={"attending": False}, headers=headers)

    assert second.status_code == 200
    assert second.json()["attending"] is False
    assert second.json()["id"] == first.json()["id"]
