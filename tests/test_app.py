import json
from unittest.mock import patch

from app import app


def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == b"Hello, Flask!"


def test_overview():
    fake_overviews = [
        {
            "code": "130000",
            "name": "東京都",
            "report_datetime": "2026-08-15T16:35:00+09:00",
            "text": "テスト概況",
        },
    ]
    with patch("app.fetch_all_overviews", return_value=fake_overviews):
        client = app.test_client()
        response = client.get("/overview")

    assert response.status_code == 200
    assert "東京都".encode() in response.data
    assert "テスト概況".encode() in response.data


def test_temperature():
    fake_points = [
        {
            "name": "東京都",
            "lat": 35.6895,
            "lon": 139.6917,
            "date": "2026-08-16",
            "min": 22,
            "max": 30,
        },
    ]
    with patch("app.fetch_all_temperatures", return_value=fake_points):
        client = app.test_client()
        response = client.get("/temperature")

    assert response.status_code == 200
    assert json.dumps("東京都").encode() in response.data
    assert b'"max": 30' in response.data
