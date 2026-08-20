from fastapi.testclient import TestClient

from main import VERSION, app


client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_info_has_all_fields():
    response = client.get("/api/info")
    assert response.status_code == 200
    assert set(response.json()) == {"version", "build_number", "theme", "hostname"}


def test_dashboard_contains_version():
    response = client.get("/")
    assert response.status_code == 200
    assert VERSION in response.text
