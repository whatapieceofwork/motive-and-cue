from flask import Flask, render_template, redirect, flash, session, request
import jinja2
import os
from bs4 import BeautifulSoup
import urllib3
import requests
import re
import pprint
import json

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]

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
    film_url = request.args.get("film-url")
    moviedb_regx = ("(?<=https:\/\/www\.themoviedb\.org\/movie\/)[0-9]*")
    moviedb_id = re.search(moviedb_regx, film_url)
    moviedb_id = moviedb_id[0]
    moviedb_credits = "https://api.themoviedb.org/3/movie/" + moviedb_id + "/credits?api_key=" + MOVIEDB_API_KEY
    credits = requests.get(moviedb_credits)
    credits = credits.json()
    cast = credits["cast"]

    actors = {}
    for actor in cast:
        actor_lname = actor["name"].split()[1].lower()
        actors[actor_lname] = actor
        print(actors[actor_lname])

    for actor in actors:
        id = actors[actor]["id"]
        actor_profile = requests.get("https://api.themoviedb.org/3/person/" + str(id) + "?api_key=" + str(MOVIEDB_API_KEY))
        actor_profile = actor_profile.json()
        actors[actor].update(actor_profile)
        print(actors[actor])


    return render_template("verify-film.html",
                            cast = cast,
                            actors = actors,
                            )


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')