from flask import Flask, render_template

from forecast import fetch_all_temperatures, fetch_weekly
from jma import fetch_all_overviews
from prefectures import PREFECTURES

app = Flask(__name__)

DEFAULT_PREFECTURE_CODE = "130000"
PREFECTURE_CODES = {pref["code"] for pref in PREFECTURES}


@app.route("/")
def index():
    return render_template("index.html", active_page="index")


@app.route("/overview")
def overview():
    overviews = fetch_all_overviews()
    return render_template("overview.html", overviews=overviews, active_page="overview")


@app.route("/temperature")
def temperature():
    points = fetch_all_temperatures()
    return render_template("temperature.html", points=points, active_page="temperature")


@app.route("/weekly/", defaults={"code": DEFAULT_PREFECTURE_CODE})
@app.route("/weekly/<code>")
def weekly(code):
    if code not in PREFECTURE_CODES:
        code = DEFAULT_PREFECTURE_CODE

    selected = next(pref for pref in PREFECTURES if pref["code"] == code)
    days = fetch_weekly(code)
    return render_template(
        "weekly.html",
        prefectures=PREFECTURES,
        selected=selected,
        days=days,
        active_page="weekly",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
