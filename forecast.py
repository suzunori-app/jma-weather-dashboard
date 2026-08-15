"""気象庁 天気予報APIから都道府県別の気温・週間天気予報を取得する。"""

import concurrent.futures
import datetime

import jpholiday
import requests

from prefectures import PREFECTURES

FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
REQUEST_TIMEOUT = 10
MAX_WORKERS = 16


def fetch_forecast(code: str) -> list | None:
    url = FORECAST_URL.format(code=code)
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def extract_min_max(forecast_json: list) -> dict | None:
    """短期予報の気温系列（県庁所在地）から最高・最低気温を取り出す。

    夕方以降に取得した場合、直近の予報対象は翌日になることがある。
    その場合は対象日を "date" として返すので、呼び出し側で表示できる。
    """
    time_series = forecast_json[0]["timeSeries"]
    temps_series = next((ts for ts in time_series if "temps" in ts["areas"][0]), None)
    if temps_series is None:
        return None

    area = temps_series["areas"][0]
    temps = [int(t) for t in area["temps"] if t]
    if len(temps) < 2:
        return None

    return {
        "date": temps_series["timeDefines"][-1][:10],
        "min": min(temps),
        "max": max(temps),
    }


def fetch_all_temperatures() -> list[dict]:
    codes = [pref["code"] for pref in PREFECTURES]
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        forecasts = dict(zip(codes, executor.map(fetch_forecast, codes), strict=True))

    points = []
    for pref in PREFECTURES:
        forecast_json = forecasts[pref["code"]]
        min_max = extract_min_max(forecast_json) if forecast_json else None
        points.append(
            {
                "name": pref["name"],
                "lat": pref["lat"],
                "lon": pref["lon"],
                "date": min_max["date"] if min_max else None,
                "min": min_max["min"] if min_max else None,
                "max": min_max["max"] if min_max else None,
            }
        )
    return points


_WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]


def _day_type(date: datetime.date) -> str:
    if date.weekday() == 6 or jpholiday.is_holiday(date):
        return "sunday-holiday"
    if date.weekday() == 5:
        return "saturday"
    return "weekday"


def _short_term_pop_for_date(forecast_json: list, date_str: str) -> int | None:
    """短期予報の降水確率系列から、指定日の最大値を取り出す。"""
    time_series = forecast_json[0]["timeSeries"]
    pop_series = next((ts for ts in time_series if "pops" in ts["areas"][0]), None)
    if pop_series is None:
        return None

    area = pop_series["areas"][0]
    pops = [
        int(pop)
        for time_define, pop in zip(pop_series["timeDefines"], area["pops"], strict=True)
        if time_define[:10] == date_str and pop
    ]
    return max(pops) if pops else None


def _fill_today_from_short_term(forecast_json: list, day: dict, date_str: str) -> None:
    """週間予報1日目は気象庁側で空欄になるため、短期予報の値で補完する。"""
    if day["precipitation_probability"] is None:
        pop = _short_term_pop_for_date(forecast_json, date_str)
        day["precipitation_probability"] = str(pop) if pop is not None else None

    if day["min"] is None or day["max"] is None:
        min_max = extract_min_max(forecast_json)
        if min_max and min_max["date"] == date_str:
            day["min"] = day["min"] or str(min_max["min"])
            day["max"] = day["max"] or str(min_max["max"])


def extract_weekly(forecast_json: list) -> list[dict]:
    """週間天気予報（県庁所在地）を日別のリストとして取り出す。"""
    weekly_time_series = forecast_json[1]["timeSeries"]
    weather_series = next(
        (ts for ts in weekly_time_series if "weatherCodes" in ts["areas"][0]), None
    )
    temps_series = next((ts for ts in weekly_time_series if "tempsMin" in ts["areas"][0]), None)
    if weather_series is None or temps_series is None:
        return []

    weather_area = weather_series["areas"][0]
    temps_area = temps_series["areas"][0]

    days = []
    for i, time_define in enumerate(weather_series["timeDefines"]):
        date_str = time_define[:10]
        date = datetime.date.fromisoformat(date_str)
        days.append(
            {
                "date_label": f"{date.month}/{date.day}",
                "weekday": _WEEKDAYS_JA[date.weekday()],
                "day_type": _day_type(date),
                "weather_code": weather_area["weatherCodes"][i],
                "precipitation_probability": weather_area["pops"][i] or None,
                "min": temps_area["tempsMin"][i] or None,
                "max": temps_area["tempsMax"][i] or None,
            }
        )

    if days:
        first_date_str = weather_series["timeDefines"][0][:10]
        _fill_today_from_short_term(forecast_json, days[0], first_date_str)

    return days


def fetch_weekly(code: str) -> list[dict]:
    forecast_json = fetch_forecast(code)
    if forecast_json is None:
        return []
    return extract_weekly(forecast_json)
