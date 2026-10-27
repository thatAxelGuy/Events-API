import os
import uuid

import pytest
import requests


@pytest.fixture
def base_url():
    return os.getenv("BASE_URL", "http://localhost:5000")

@pytest.fixture
def unique_username():
    return f"testuser_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def auth_token(base_url, unique_username):
    password = "test_password_123"
    credentials = {"username": unique_username, "password": password}

    register_response = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert register_response.status_code == 201

    login_response = requests.post(f"{base_url}/api/auth/login", json=credentials)
    assert login_response.status_code == 200

    return login_response.json()["access_token"]

