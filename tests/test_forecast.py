import datetime

from forecast import _day_type, extract_weekly


def test_day_type_sunday():
    assert _day_type(datetime.date(2024, 1, 7)) == "sunday-holiday"


def test_day_type_saturday():
    assert _day_type(datetime.date(2024, 1, 6)) == "saturday"


def test_day_type_holiday_on_weekday():
    assert _day_type(datetime.date(2024, 1, 1)) == "sunday-holiday"


def test_day_type_weekday():
    assert _day_type(datetime.date(2024, 1, 9)) == "weekday"


def test_extract_weekly_fills_first_day_from_short_term():
    """週間予報1日目は気象庁側で空欄になるため、短期予報の値で補完されることを確認する。"""
    forecast_json = [
        {
            "timeSeries": [
                {"timeDefines": [], "areas": [{"area": {"name": "東京地方", "code": "130010"}}]},
                {
                    "timeDefines": [
                        "2024-01-06T18:00:00+09:00",
                        "2024-01-07T00:00:00+09:00",
                        "2024-01-07T06:00:00+09:00",
                        "2024-01-07T12:00:00+09:00",
                        "2024-01-07T18:00:00+09:00",
                    ],
                    "areas": [
                        {
                            "area": {"name": "東京地方", "code": "130010"},
                            "pops": ["10", "10", "0", "20", "10"],
                        }
                    ],
                },
                {
                    "timeDefines": ["2024-01-07T00:00:00+09:00", "2024-01-07T09:00:00+09:00"],
                    "areas": [{"area": {"name": "東京", "code": "44132"}, "temps": ["3", "10"]}],
                },
            ]
        },
        {
            "timeSeries": [
                {
                    "timeDefines": ["2024-01-07T00:00:00+09:00", "2024-01-08T00:00:00+09:00"],
                    "areas": [
                        {
                            "area": {"name": "東京地方", "code": "130010"},
                            "weatherCodes": ["100", "200"],
                            "pops": ["", "30"],
                            "reliabilities": ["", "A"],
                        }
                    ],
                },
                {
                    "timeDefines": ["2024-01-07T00:00:00+09:00", "2024-01-08T00:00:00+09:00"],
                    "areas": [
                        {
                            "area": {"name": "東京", "code": "44132"},
                            "tempsMin": ["", "2"],
                            "tempsMax": ["", "9"],
                        }
                    ],
                },
            ]
        },
    ]

    days = extract_weekly(forecast_json)

    assert days[0]["date_label"] == "1/7"
    assert days[0]["precipitation_probability"] == "20"
    assert days[0]["min"] == "3"
    assert days[0]["max"] == "10"
    assert days[1]["precipitation_probability"] == "30"
