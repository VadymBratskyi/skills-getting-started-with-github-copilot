import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_serves_html():
    response = client.get("/")
    # Should serve the HTML page directly (status 200)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert b"Mergington High School" in response.content

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_for_activity_success():
    # Use a unique email to avoid duplicate error
    email = "pytestuser@mergington.edu"
    activity = "Chess Club"
    # Remove if already present
    client.post(f"/activities/{activity}/signup?email={email}")
    # Now sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    if response.status_code == 400:
        # Already signed up, so remove and try again
        from src.app import app as fastapi_app
        fastapi_app.activities[activity]["participants"].remove(email)
        response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json()["message"]

def test_signup_for_activity_duplicate():
    email = "pytestdupe@mergington.edu"
    activity = "Programming Class"
    # Ensure signed up
    client.post(f"/activities/{activity}/signup?email={email}")
    # Try again, should fail
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_for_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]