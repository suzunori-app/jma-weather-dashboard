"""気象庁 天気予報APIから都道府県別の最高・最低気温を取得する。"""

import concurrent.futures

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
