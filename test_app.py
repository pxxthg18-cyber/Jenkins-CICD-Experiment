"""
test_app.py - Automated test suite for the Flask web application using pytest.

This file is automatically executed during the 'Test' stage of the Jenkins CI/CD pipeline.
"""

import pytest
from app import app


@pytest.fixture
def client():
    """
    Creates and configures a Flask test client instance for testing.
    This fixture runs before each test function that requests it.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page_status_code(client):
    """Verify that the home page ('/') responds with HTTP 200 OK."""
    response = client.get("/")
    assert response.status_code == 200


def test_home_page_content(client):
    """Verify that the home page contains essential experiment titles and badges."""
    response = client.get("/")
    html_content = response.data.decode("utf-8")
    assert "Jenkins CI/CD Lab Experiment" in html_content
    assert "jenkins-cicd-flask-app" in html_content
    assert "Check Health API" in html_content


def test_health_endpoint_status(client):
    """Verify that the '/health' endpoint responds with HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_json_payload(client):
    """Verify that the '/health' endpoint returns the expected JSON structure."""
    response = client.get("/health")
    assert response.is_json
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["app"] == "jenkins-cicd-flask-app"
    assert data["version"] == "1.0.0"


def test_invalid_route_returns_404(client):
    """Verify that requesting an unregistered route returns HTTP 404 Not Found."""
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404
