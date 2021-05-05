from flask import Flask, render_template, redirect, flash, session, request
import jinja2
import os
from bs4 import BeautifulSoup
import urllib3

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIE_API_KEY = os.environ["MOVIE_API_KEY"]

app = Flask(__name__)

app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.secret_key = FLASK_KEY

plays = {
    "hamlet": "Hamlet",
}

@app.route("/")
def index():
    """Displays index page."""

    return render_template("index.html")


@app.route("/add-film")
def add_film():
    """Prompts user for play and IMDB ID."""

    return render_template("add-film.html",
                            plays = plays)


@app.route("/process-film")
def process_film():
    """Processes user input, scrapes IMDB for information."""

    play = request.args.get("play")
    imdb_url = request.args.get("imdb-url")
    http = urllib3.PoolManager()
    page = http.request("GET", imdb_url)
    status = page.status

    return render_template("verify-film.html",
                            status = status)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')