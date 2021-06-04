from flask import Flask, render_template, redirect, flash, session, request
from flask_sqlalchemy import SQLAlchemy
import jinja2
import os
import requests
import re #regex
import json

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]

app = Flask(__name__)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.secret_key = FLASK_KEY

db = SQLAlchemy()

plays = {"Hamlet": "Hamlet"}

@app.route("/")
def index():
    """Displays index page."""

    return render_template("index.html")


@app.route("/add-film")
def add_film():
    """Prompts user for play and MovieDB ID."""

    return render_template("add-film.html",
                            plays = plays)


@app.route("/process-film")
def process_film():
    """Processes user input, scrapes MovieDB for information."""

    play = request.args.get("play")
    film_url = request.args.get("film-url")
    moviedb_regx = ("(?<=https:\/\/www\.themoviedb\.org\/movie\/)[0-9]*")
    moviedb_id = re.search(moviedb_regx, film_url)
    moviedb_id = moviedb_id[0]
    moviedb_credits = "https://api.themoviedb.org/3/movie/" + moviedb_id + "/credits?api_key=" + MOVIEDB_API_KEY
    credits = requests.get(moviedb_credits)
    credits = credits.json()
    print(credits)
    cast = credits["cast"]
    crew = credits["crew"]

    for member in crew:
        if crew[member]["job"] == "Director":
            moviedb_id = crew[member]["id"]
            full_name = crew[member]["name"].split()
            fname, lname = full_name[0], full_name[-1]

            # director = crud.add_new_director(moviedb_id, fname, lname)
            # crud.add_director_film(director, film)

    actors = {}
    for actor in cast:
        actor_lname = actor["name"].split()[1].lower()
        actors[actor_lname] = actor

    for actor in actors:
        moviedb_id = actors[actor]["id"]
        actor_profile = requests.get("https://api.themoviedb.org/3/person/" + str(moviedb_id) + "?api_key=" + MOVIEDB_API_KEY)
        actor_profile = actor_profile.json()
        actors[actor].update(actor_profile) #add entire JSON actor profile to actor dictionary

        parts_played = actors[actor]["character"].split(" / ")
        # for part in parts_played,
            # add a row to casting table
        
        full_name = actors[actor]["name"].split()
        fname, lname = full_name[0], full_name[-1]

        if actors[actor]["gender"] == 2:
            gender = "Male"
        elif actors[actor]["gender"] == 1:
            gender = "Female"
        else:
            gender = "Other or N/A"

    return render_template("verify-film.html",
                            cast = cast,
                            actors = actors,
                            )


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')