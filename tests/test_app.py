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
