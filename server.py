from flask import Flask, render_template, redirect, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from bs4 import BeautifulSoup
from datetime import datetime
import jinja2
import os
import requests
import re #regex
import json
import crud
from data_model import *

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()


app = Flask(__name__)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.secret_key = FLASK_KEY


plays = {
	"Ham": "Hamlet",
}

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

    shortname = request.args.get("play")
    # play = crud.add_play(plays[shortname], shortname)
    play = crud.add_play("Hamlet", "Ham")
    play_id = play.play_id

    film_url = request.args.get("film-url")
    moviedb_regx = ("(?<=https:\/\/www\.themoviedb\.org\/movie\/)[0-9]*") #MovieDB film ID format
    moviedb_id = re.search(moviedb_regx, film_url)[0] #first result of regex search for MovieDB film ID format in URL
    moviedb_id = int(moviedb_id)
    moviedb_credits = "https://api.themoviedb.org/3/movie/" + str(moviedb_id) + "/credits?api_key=" + MOVIEDB_API_KEY
    credits = requests.get(moviedb_credits).json()
    cast_credits, crew_credits = credits["cast"], credits["crew"]

    film = crud.process_moviedb_film_details(moviedb_id, play) #process MovieDB film details and create Film database object
    crud.process_moviedb_cast(moviedb_id, cast_credits, play) #process MovieDB actor details and create Actor database objects
    crud.process_moviedb_crew(moviedb_id, crew_credits, play) #process MovieDB crew details and create various crew database objects

    return render_template("verify-film.html")


if __name__ == '__main__':
    app.debug = True
    connect_to_db(app)
    app.run(host='0.0.0.0')