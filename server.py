from flask import Flask, render_template, redirect, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.sql import exists
from bs4 import BeautifulSoup
from datetime import datetime
import jinja2
import os
import requests
import json
from crud import *
from data_model import *
from folger_parser import *
from moviedb_parser import *
from seed import *

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()

app = Flask(__name__)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.secret_key = FLASK_KEY

Bootstrap(app)

@app.route("/")
def index():
    """Displays index page."""

    return render_template("index.html")


@app.route("/choose-play")
def choose_play():
    """Prompts user for play name, passes to appropriate function."""

    return render_template("choose-play.html",
                            play_titles = play_titles)


# ----- BEGIN: PROCESS SCENES ----- #

@app.route("/add-scenes")
def add_scenes():
    """Prompts user for play name to add scenes via the Folger page of that play."""

    return render_template("choose-play.html",
                            function="add_scenes",
                            play_titles = play_titles)


@app.route("/process-scenes-by-play")
def process_scenes():
    """Given a Shakespeare play by the user, query the Folger website and scrape a list of scenes."""

    play_shortname = request.args.get("play_titles")
    play = get_play_by_shortname(play_shortname)

    scenes = parse_folger_scene_descriptions(play)

    return render_template("scenes-verify.html",
                            play=play,
                            scenes=scenes)


@app.route("/add-scenes-to-db", methods = ["POST"])
def add_scenes_to_db():
    """Use the form data from /process-scenes to add scene information to the database."""

    play_title = request.form.get("play")
    play = get_play_by_title(play_title)
    scene_count = request.form.get("scene_count")
    scene_count = int(scene_count) + 1

    scenes = {}
    for i in range(scene_count):
        scene = {}
        scene["act"] = request.form.get(f"act-{i}")
        scene["scene"] = request.form.get(f"scene-{i}")
        scene["title"] = request.form.get(f"title-{i}")
        scene["description"] = request.form.get(f"description-{i}")
        scene["quote"] = request.form.get(f"quote-{i}")
        scenes[i] = scene

        db_scene = get_scene(act=scene["act"], scene=scene["scene"], play=play, title=scene["title"], description=scene["description"], quote=scene["quote"])

    return f"<div>{scenes}</div>"


@app.route("/edit-scenes")
def edit_scenes():
    """Prompts user for play name to edit scenes via the Folger page of that play."""

    return render_template("choose-play.html",
                            function="edit_scenes",
                            play_titles = play_titles)


@app.route("/edit-scenes-by-play")
def edit_scenes_by_play():
    """Given a Shakespeare play by the user, edit the existing scenes in the database."""

    play_shortname = request.args.get("play_titles")
    play = get_play_by_shortname(play_shortname)

    scenes = get_all_scenes_by_play(play)

    return render_template("scenes-edit.html",
                            play=play,
                            scenes=scenes)


@app.route("/edit-scenes-in-db", methods = ["POST"])
def edit_scenes_in_db():
    """Use the form data from /edit-scenes to edit scene information to the database."""

    play_title = request.form.get("play")
    play = get_play_by_title(play_title)
    scene_count = request.form.get("scene_count")
    scene_count = int(scene_count) + 1

    scenes = {}
    for i in range(scene_count):
        scene_id = request.form.get(f"id-{i}")
        scene = Scene.query.get(scene_id)
        title = request.form.get(f"title-{i}")
        description = request.form.get(f"description-{i}")
        if title or description:
            update_scene(scene, title, description)

    return f"<div>{scenes}</div>"


@app.route("/view-scenes")
def view_scenes():
    """Prompts user for play name to view a list of associated scenes."""

    return render_template("choose-play.html",
                            function = "view_scenes",
                            play_titles = play_titles)


@app.route("/view-scenes-by-play", methods = ["GET"])
def view_scenes_by_play():
    """Given a Shakespeare play by the user, view a list of associated scenes."""

    play_shortname = request.args.get("play_titles")
    play = get_play_by_shortname(play_shortname)

    scenes = get_all_scenes_by_play(play)

    return render_template("scenes-all.html",
                            play=play,
                            scenes=scenes)

# ----- END: PROCESS SCENES ----- #


# ----- BEGIN: PROCESS CHARACTERS ----- #

@app.route("/add-characters")
def add_characters():
    """Prompts user for play name to add play characters via API."""

    return render_template("characters-add.html",
                            play_titles = play_titles)


@app.route("/process-characters")
def process_characters():
    """Given a Shakespeare play by the user, query the Folger Shakespeare API for a list of characters."""

    play_shortname = request.args.get("play_titles")
    play = get_play_by_shortname(play_shortname)

    characters = parse_folger_characters(play)

    return render_template("characters-verify.html",
                            play=play,
                            characters=characters,
                            genders=GENDERS)


@app.route("/add-characters-to-db", methods = ["POST"])
def add_characters_to_db():
    """Use the form data from /process-characters to add character information to the database."""

    play_title = request.form.get("play")
    play = get_play_by_title(play_title)
    characters = []
    character_count = request.form.get("character_count")
    character_count = int(character_count) + 1
    for i in range(character_count):
        character = {}
        character["name"] = request.form.get(f"name-{i}")
        character["gender"] = request.form.get(f"gender-{i}")

        db_character = get_character(name=character["name"], gender=character["gender"], play=play)
        characters.append(character)

    return f"<div>{characters}</div>"

# ----- END: PROCESS CHARACTERS ----- #


# ----- BEGIN: PROCESS FILM ----- #

@app.route("/add-film")
def add_new_film():
    """Prompts user for play and MovieDB ID to add film information via API."""

    return render_template("film-add.html",
                            play_titles = play_titles)


@app.route("/process-film")
def process_film():
    """Given a MovieDB film URL by the user, query the MovieDB API for film info and pass to verification page."""

    play_shortname = request.args.get("play_titles")
    play = get_play_by_shortname(play_shortname)
    film_url = request.args.get("film-url")

    film_id = get_moviedb_film_id(film_url)
    details, cast, crew = parse_moviedb_film(film_id, play)

    character_names = [character.name for character in play.characters]
    character_names.sort()

    return render_template("film-verify.html",
                            details=details,
                            cast=cast,
                            crew=crew,
                            play=play,
                            genders=GENDERS,
                            character_names=character_names,
                            )


@app.route("/add-film-to-db", methods = ["POST"])
def add_film_to_db():
    """Use the form data from /process-film to add film information to the database."""

    film = {}
    film["play"] = request.form.get("play")
    film["title"] = request.form.get("title")
    film["poster_path"] = request.form.get("poster_path")
    film["release_date"] = request.form.get("release_date")
    film["language"] = request.form.get("language")
    film["length"] = request.form.get("length")
    film["film_moviedb_id"] = request.form.get("film_moviedb_id")
    film["film_imdb_id"] = request.form.get("film_imdb_id")

    play = get_play_by_title(film["play"])
    db_film = get_film(play=play, moviedb_id=film["film_moviedb_id"], imdb_id=film["film_imdb_id"], title=film["title"], release_date=film["release_date"], language=film["language"], length=film["length"], poster_path=film["poster_path"])
    
    people = []
    person_count = request.form.get("person_count")
    person_count = int(person_count) + 1
    for i in range(person_count):
        person = {}
        person["exclude"] = request.form.get(f"exclude-{i}")

        if not person["exclude"]:
            person["fname"] = request.form.get(f"fname-{i}")
            person["lname"] = request.form.get(f"lname-{i}")
            person["photo_path"] = request.form.get(f"photo_path-{i}")
            person["birthday"] = request.form.get(f"birthday-{i}")
            if not person["birthday"]:
                person["birthday"] = None
            person["gender"] = request.form.get(f"gender-{i}")
            person["moviedb_id"] = request.form.get(f"person_moviedb_id-{i}")
            person["imdb_id"] = request.form.get(f"person_imdb_id-{i}")

            person["parts"] = []
            part_count = request.form.get(f"part_count-{i}")
            part_count = int(part_count) + 1
            for j in range(part_count):
                person["parts"].append(request.form.get(f"part-{i}-{j}"))

            db_person = get_person(person["moviedb_id"], person["imdb_id"], person["fname"], person["lname"], person["birthday"], person["gender"], person["photo_path"])
            if person["parts"]:
                get_job_held(db_person, db_film, "Actor")
            for part_name in person["parts"]:
                get_part_played(person=db_person, character_name=part_name, film=db_film)

            people.append(person)

    return render_template("submit-form.html",
                            film=film,
                            people=people)

# ----- END: PROCESS FILM ----- #

    
if __name__ == '__main__':
    app.debug = True
    connect_to_db(app)
    app.run(host='0.0.0.0')
    seed_hamlet()