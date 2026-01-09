from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities before and after each test."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_creates_participant():
    email = "tester@example.com"
    activity = "Chess Club"
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Ensure participant appears in GET
    data = client.get("/activities").json()
    assert email in data[activity]["participants"]


def test_duplicate_signup_returns_400():
    email = "michael@mergington.edu"
    activity = "Chess Club"
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 400


def test_unregister_removes_participant():
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Unregister
    resp = client.delete(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    data = client.get("/activities").json()
    assert email not in data[activity]["participants"]


def test_unregister_not_signed_up_returns_400():
    email = "nobody@example.com"
    activity = "Chess Club"

    resp = client.delete(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 400


def test_nonexistent_activity_returns_404_for_signup_and_unregister():
    email = "a@b.com"
    activity = "Nonexistent Activity"
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 404

    resp = client.delete(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 404
