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
from crud import *
from data_model import *

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()


app = Flask(__name__)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.secret_key = FLASK_KEY


play_titles = {"AWW": "All's Well That Ends Well", "Ant": "Antony and Cleopatra", "AYL": "As You Like It", "Err": "The Comedy of Errors", "Cor": "Coriolanus", "Cym": "Cymbeline", "Ham": "Hamlet", "1H4": "Henry IV, Part 1", "2H4": "Henry IV, Part 2", "H5": "Henry V", "1H6": "Henry VI, Part 1", "2H6": "Henry VI, Part 2", "3H6": "Henry VI, Part 3", "H8": "Henry VIII", "JC": "Julius Caesar", "Jn": "King John", "Lr": "King Lear", "LLL": "Love's Labor's Lost", "Mac": "Macbeth", "MM": "Measure for Measure", "MV": "The Merchant of Venice", "Wiv": "The Merry Wives of Windsor", "MND": "A Midsummer Night's Dream", "Ado": "Much Ado About Nothing", "Oth": "Othello", "Per": "Pericles", "R2": "Richard II", "R3": "Richard III", "Rom": "Romeo and Juliet", "Shr": "The Taming of the Shrew", "Tmp": "The Tempest", "Tim": "Timon of Athens", "Tit": "Titus Andronicus", "Tro": "Troilus and Cressida", "TN": "Twelfth Night", "TGV": "Two Gentlemen of Verona", "TNK": "Two Noble Kinsmen", "WT": "The Winter's Tale"}

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

    play_shortname = request.args.get("plays")
    play = get_play_by_shortname(play_shortname)
    
    film_url = request.args.get("film-url")
    moviedb_regx = ("(?<=https:\/\/www\.themoviedb\.org\/movie\/)[0-9]*") #MovieDB film ID format
    moviedb_id = re.search(moviedb_regx, film_url)[0] #first result of regex search for MovieDB film ID format in URL
    moviedb_id = int(moviedb_id)
    moviedb_credits = "https://api.themoviedb.org/3/movie/" + str(moviedb_id) + "/credits?api_key=" + MOVIEDB_API_KEY
    credits = requests.get(moviedb_credits).json()
    cast_credits, crew_credits = credits["cast"], credits["crew"]

    process_moviedb_film_details(moviedb_id, play) #process MovieDB film details and create Film database object
    process_moviedb_cast(moviedb_id, cast_credits, play) #process MovieDB actor details and create Actor database objects
    process_moviedb_crew(moviedb_id, crew_credits, play) #process MovieDB crew details and create various crew database objects

    return render_template("verify-film.html")


if __name__ == '__main__':
    app.debug = True
    connect_to_db(app)
    app.run(host='0.0.0.0')