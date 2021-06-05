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
    """Given MovieDB URL by user, queries MovieDB API for film information and adds information to database."""

    play = request.args.get("play")
    film_url = request.args.get("film-url")
    moviedb_regx = ("(?<=https:\/\/www\.themoviedb\.org\/movie\/)[0-9]*") #MovieDB film ID format
    moviedb_id = re.search(moviedb_regx, film_url)[0] #first result of regex search for MovieDB film ID format in URL
    moviedb_credits = "https://api.themoviedb.org/3/movie/" + moviedb_id + "/credits?api_key=" + MOVIEDB_API_KEY
    credits = requests.get(moviedb_credits).json()
    cast_credits, crew_credits = credits["cast"], credits["crew"]

    film = crud.process_moviedb_film_details(moviedb_id) #process MovieDB film details and create Film database object
    cast  = crud.process_moviedb_film_cast(moviedb_id, cast_credits) #process MovieDB actor details and create Actor database objects
    crew = crud.process_moviedb_film_crew(moviedb_id, crew_credits) #process MovieDB crew details and create various crew database objects

    return render_template("verify-film.html"
                            )


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')