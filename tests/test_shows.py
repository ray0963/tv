import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_token():
    """Get authentication token for testing"""
    response = client.post(
        "/auth/login", json={"username": "ray", "password": "password123"}
    )
    return response.json()["access_token"]


def test_create_show():
    """Test creating a show"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/shows/", json={"title": "Test Show"}, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Show"
    assert "id" in data


def test_create_duplicate_show():
    """Test creating a show with duplicate title"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create first show
    client.post("/shows/", json={"title": "Duplicate Show"}, headers=headers)

    # Try to create duplicate
    response = client.post("/shows/", json={"title": "Duplicate Show"}, headers=headers)
    assert response.status_code == 400


def test_list_shows():
    """Test listing shows"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/shows/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_watch_show():
    """Test marking a show as watched"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First create a show
    show_response = client.post(
        "/shows/", json={"title": "Show to Watch"}, headers=headers
    )
    show_id = show_response.json()["id"]

    # Mark as watched
    response = client.post(
        f"/shows/{show_id}/watch", json={"rating": 5}, headers=headers
    )
    assert response.status_code == 201


def test_watch_show_invalid_rating():
    """Test watching a show with invalid rating"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a show
    show_response = client.post(
        "/shows/", json={"title": "Show for Rating Test"}, headers=headers
    )
    show_id = show_response.json()["id"]

    # Try invalid rating
    response = client.post(
        f"/shows/{show_id}/watch", json={"rating": 6}, headers=headers
    )
    assert response.status_code == 400
