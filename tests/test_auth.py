import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    """Test successful login"""
    response = client.post("/auth/login", json={
        "username": "ray",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"] == "ray"

def test_login_failure():
    """Test failed login"""
    response = client.post("/auth/login", json={
        "username": "ray",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_invalid_user():
    """Test login with non-existent user"""
    response = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "password123"
    })
    assert response.status_code == 401

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "TV Show Tracker API"
    assert "ray" in data["users"]
    assert "dana" in data["users"]
