from flask import Flask, render_template

from forecast import fetch_all_temperatures
from jma import fetch_all_overviews

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, Flask!"


@app.route("/overview")
def overview():
    overviews = fetch_all_overviews()
    return render_template("overview.html", overviews=overviews, active_page="overview")


@app.route("/temperature")
def temperature():
    points = fetch_all_temperatures()
    return render_template("temperature.html", points=points, active_page="temperature")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
