import json
from unittest.mock import patch

from app import app


def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "気象庁 天気ダッシュボード".encode() in response.data
    assert b'class="tabs"' in response.data


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


def test_weekly():
    fake_days = [
        {
            "date_label": "8/16",
            "weekday": "日",
            "day_type": "sunday-holiday",
            "weather_code": "200",
            "precipitation_probability": "30",
            "min": "22",
            "max": "30",
        },
    ]
    with patch("app.fetch_weekly", return_value=fake_days):
        client = app.test_client()
        response = client.get("/weekly/270000")

    assert response.status_code == 200
    assert "東京都".encode() in response.data
    assert "200.svg".encode() in response.data
    assert "30%".encode() in response.data
    assert "8/16（日）".encode() in response.data
    assert b'class="sunday-holiday"' in response.data


def test_weekly_unknown_pref_falls_back_to_default():
    with patch("app.fetch_weekly", return_value=[]):
        client = app.test_client()
        response = client.get("/weekly/999999")

    assert response.status_code == 200
    assert "東京都".encode() in response.data
