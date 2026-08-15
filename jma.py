"""気象庁 防災情報XML/JSON APIから予報区別の気象概況を取得する。"""

import concurrent.futures

import requests

from areas import OFFICES

OVERVIEW_URL = "https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{code}.json"
REQUEST_TIMEOUT = 10
MAX_WORKERS = 16


def fetch_overview(code: str) -> dict | None:
    url = OVERVIEW_URL.format(code=code)
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def fetch_all_overviews() -> list[dict]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = dict(zip(OFFICES, executor.map(fetch_overview, OFFICES), strict=True))

    return [
        {
            "code": code,
            "name": name,
            "report_datetime": (results[code] or {}).get("reportDatetime"),
            "text": (results[code] or {}).get("text"),
        }
        for code, name in OFFICES.items()
    ]
