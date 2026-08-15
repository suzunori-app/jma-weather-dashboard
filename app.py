from flask import Flask, render_template

from jma import fetch_all_overviews

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, Flask!"


@app.route("/overview")
def overview():
    overviews = fetch_all_overviews()
    return render_template("overview.html", overviews=overviews)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
