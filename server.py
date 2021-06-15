from flask import Flask, render_template, redirect, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.sql import exists
from bs4 import BeautifulSoup
from datetime import datetime
import jinja2
import os
import requests
import re #regex
import json
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from crud import *
from data_model import *
from folger_parser import *
from moviedb_parser import *
from forms import *

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()

app = Flask(__name__)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.secret_key = FLASK_KEY

Bootstrap(app)

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
    """Given a MovieDB film URL by the user, query the MovieDB API for film info and pass to verification page."""

    play_shortname = request.args.get("plays")
    play = get_play_by_shortname(play_shortname)
    film_url = request.args.get("film-url")

    film_id = get_moviedb_film_id(film_url)
    details, cast, crew = parse_moviedb_film(film_id, play)

    # # form = ValidateMovieDBInfo(details, cast, crew)

    # return render_template("test-form.html",
    #                         form=form)

    return render_template("verify-film.html",
                            details=details,
                            cast=cast,
                            crew=crew,
                            play=play,
                            genders=GENDERS)


@app.route("/add-film-to-db", methods = ["POST"])
def add_film_to_db():
    """Use the form data from /process-film to add film information to the database."""

    film = {}
    film["title"] = request.form.get("title")
    film["poster_path"] = request.form.get("poster_path")
    film["release_date"] = request.form.get("release_date")
    film["language"] = request.form.get("language")
    film["length"] = request.form.get("length")
    film["film_moviedb_id"] = request.form.get("film_moviedb_id")
    film["film_imdb_id"] = request.form.get("film_imdb_id")

    people = []
    person_count = request.form.get("person_count")
    person_count = int(person_count) + 1
    for i in range(person_count):
        person = {}
        person["fname"] = request.form.get(f"fname-{i}")
        person["lname"] = request.form.get(f"lname-{i}")
        person["photo_path"] = request.form.get(f"photo_path-{i}")
        person["birthday"] = request.form.get(f"birthday-{i}")
        person["gender"] = request.form.get(f"gender-{i}")
        person["person_moviedb_id"] = request.form.get(f"person_moviedb_id-{i}")
        person["person_imdb_id"] = request.form.get(f"person_imdb_id-{i}")

        person["parts"] = []
        part_count = request.form.get(f"part_count-{i}")
        part_count = int(part_count) + 1
        for j in range(part_count):
            person["parts"].append(request.form.get(f"part-{i}-{j}"))

        people.append(person)

    return render_template("submit-form.html",
                            film=film,
                            people=people)



# @app.route("/test-form", methods=["GET", "POST"])
# def contact():
#    form = ValidateMovieDBInfo()
#    return render_template('test-form.html', form=form)

# @app.route('/test-submit', methods=['GET', 'POST'])
# def test_submit():
#     form = ValidateMovieDBInfo()
#     if form.validate_on_submit():
#         title = form.title.data
#         release_date = form.release_date.data  
#         flash(f"{title}, {release_date}, {date2}")
#         return redirect("/")
#     else:
#         return render_template('test-submit.html', form=form)
    
if __name__ == '__main__':
    app.debug = True
    connect_to_db(app)
    app.run(host='0.0.0.0')