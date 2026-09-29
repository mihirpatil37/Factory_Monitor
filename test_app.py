from unittest.mock import patch
import app


def test_latest_endpoint_deduplicates_by_topic():
    # Fake rows shaped exactly like get_latest_readings() would return them,
    # so the test never touches MQTT or a real database.
    fake_rows = [
        ("factory/line1/machine1/temperature", "75.0", "2026-09-29 10:00:05"),
        ("factory/line1/machine1/temperature", "74.0", "2026-09-29 10:00:03"),
        ("factory/line1/machine1/pressure", "2.1", "2026-09-29 10:00:04"),
    ]

    with patch("app.get_latest_readings", return_value=fake_rows):
        client = app.app.test_client()
        response = client.get("/api/latest")
        data = response.get_json()

    assert response.status_code == 200
    assert data["temperature"]["value"] == "75.0"  # first occurrence wins
    assert data["pressure"]["value"] == "2.1"
    assert "status" not in data  # no status reading was mocked in


def test_home_route_returns_running_message():
    client = app.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Factory Monitor is running" in response.data
