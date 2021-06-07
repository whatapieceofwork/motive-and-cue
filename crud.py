"""Create, Read, Update, Delete Operations. Listed alphabetically."""

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
from data_model import *

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()

plays = {"AWW": "All's Well That Ends Well", "Ant": "Antony and Cleopatra", "AYL": "As You Like It", "Err": "The Comedy of Errors", "Cor": "Coriolanus", "Cym": "Cymbeline", "Ham": "Hamlet", "1H4": "Henry IV, Part 1", "2H4": "Henry IV, Part 2", "H5": "Henry V", "1H6": "Henry VI, Part 1", "2H6": "Henry VI, Part 2", "3H6": "Henry VI, Part 3", "H8": "Henry VIII", "JC": "Julius Caesar", "Jn": "King John", "Lr": "King Lear", "LLL": "Love's Labor's Lost", "Mac": "Macbeth", "MM": "Measure for Measure", "MV": "The Merchant of Venice", "Wiv": "The Merry Wives of Windsor", "MND": "A Midsummer Night's Dream", "Ado": "Much Ado About Nothing", "Oth": "Othello", "Per": "Pericles", "R2": "Richard II", "R3": "Richard III", "Rom": "Romeo and Juliet", "Shr": "The Taming of the Shrew", "Tmp": "The Tempest", "Tim": "Timon of Athens", "Tit": "Titus Andronicus", "Tro": "Troilus and Cressida", "TN": "Twelfth Night", "TGV": "Two Gentlemen of Verona", "TNK": "Two Noble Kinsmen", "WT": "The Winter's Tale"}


def add_character(name, play):
    """Create and return a new Character database record."""

    character = Character(name=name, play_id=play.id)

    db.session.add(character)
    db.session.commit()

    print(f"********* Created {character} *********")
    return character


def add_film(play, moviedb_id, imdb_id, title, release_date, language, length, poster_path):
    """Create and return a new Film database record."""

    film = Film(play_id=play.id, moviedb_id=moviedb_id, imdb_id=imdb_id, title=title, release_date=release_date, language=language, length=length, poster_path=poster_path)

    db.session.add(film)
    db.session.commit()

    print(f"Created {film} *********")
    return film


def add_job(title):
    """Create and returned a Job database record."""

    job = Job(title=title)

    db.session.add(job)
    db.session.commit()

    print(f"********* Created {job} *********")
    return job


def add_job_held(film, job, person):
    """Create and returned a JobHeld database record."""

    jobheld = JobHeld(film_id=film.id, job_id=job.id, person_id=person.id)
    
    db.session.add(jobheld)
    db.session.commit()

    print(f"********* Created {jobheld} *********")
    return jobheld


def add_part_played(person, character, film):
    """Create and return a PartPlayed database relationship record."""

    # if not character:
    #     play = get_play_by_film(film)
    #     character = add_character(character, play)
    part_played=PartPlayed(person_id=person.id, character_id=character.id, film_id=film.id)

    db.session.add(part_played)
    db.session.commit()

    print(f"********* Created {part_played} *********")
    return part_played
    

def add_person(moviedb_id, imdb_id, fname, lname, birthday, gender, photo_path):
    """Create and a return a new Person database record."""

    person = Person(moviedb_id=moviedb_id, imdb_id=imdb_id, fname=fname, lname=lname,
                    birthday=birthday, gender=gender, photo_path=photo_path)

    db.session.add(person)
    db.session.commit()

    print(f"********* Created {person} *********")
    return person


def add_play(title, shortname):
    """Create and return a new Play database record."""

    play = Play(title=title, shortname=shortname)
    db.session.add(play)
    db.session.commit()

    print(f"********* Created {play} *********")
    return play


def add_scene(act, scene, title):
    """Create and return a new Scene database record."""

    scene = Scene(act=act, scene=scene, title=title)
    db.session.add(scene)
    db.session.commit()

    print(f"********* Created {scene} *********")
    return scene


def add_topic(title, desc, quote):
    """Create and return a new Topic database record."""

    topic = Topic(title=title, desc=desc, quote=quote)

    db.session.add(topic)
    db.session.commit()

    print(f"********* Created {topic} *********")
    return topic


def process_folger_characters(play):
    """Given a play shortname, import the Folger list of characters by line count."""

    from bs4 import BeautifulSoup
    import requests

    shortname = play.shortname
    parts_page_url = f"https://folgerdigitaltexts.org/{shortname}/parts/"
    page = requests.get(parts_page_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    character_link_list = soup.find("a")

    for link in character_link_list:
        name = link.text
        if name.istitle():
          character = get_character_by_name(name, play.id)

    db.session.commit()


def process_moviedb_cast(moviedb_id, cast_credits, play):
    """Given a MovieDB ID and cast credits JSON object, process cast info and create Person database records."""

    film = get_film_by_moviedb_id(moviedb_id, play)

    for castmember in cast_credits:
            person_moviedb_id = castmember["id"]
            person = get_person_by_moviedb_id(person_moviedb_id)
            parts_played = castmember["character"].split(" / ")
        
            for part in parts_played:
                character = get_character_by_name(part, play)
                part_played = add_part_played(person, character, film)
                db.session.add(part_played)

    db.session.commit() 


def process_moviedb_crew(moviedb_id, crew_credits, play):
    """Given a Movie record and crew credits JSON object, process crew info and create important crew database records."""

    important_crew = {"Director", "Cinematographer", "Executive Producer", "Writer"}
    film = get_film_by_moviedb_id(moviedb_id, play)

    for crewmember in crew_credits:
        if crewmember["job"] in important_crew:
            crew_moviedb_id = crewmember["id"]
            person = get_person_by_moviedb_id(crew_moviedb_id)
            job = get_job_by_title(crewmember["job"])
            jobheld = add_job_held(film, job, person)

            db.session.add(jobheld)
    
    db.session.commit()


def process_moviedb_film_details(moviedb_id, play):
    """Given a MovieDB ID, query film information from MovieDB and create a Film database record."""

    film_details = "https://api.themoviedb.org/3/movie/" + str(moviedb_id) + "?api_key=" + MOVIEDB_API_KEY + "&language=en-US"
    details = requests.get(film_details).json()
    imdb_id = details["imdb_id"]
    title = details["title"]
    release_date = details["release_date"]
    format = "%Y-%m-%d"
    release_date = datetime.strptime(release_date, format)
    language = details["original_language"]
    length = details["runtime"]
    poster_path = details["poster_path"]
    play_id = play.id

    film = add_film(play=play, moviedb_id=moviedb_id, imdb_id=imdb_id, title=title, release_date=release_date, language=language, length=length, poster_path=poster_path)
    return film


def get_character_by_name(name, play):
    """Given a character name and play, return the Character object."""

    existing_record = db.session.query(exists().where((Character.name == name) & (Character.play_id == play.id))).scalar()
    if existing_record:
        return Character.query.filter((Character.name == name) & (Character.play_id == play.id)).first()
    else:
        character = add_character(name=name, play=play)
        return character

def get_job_by_title(title):
    """Given a job title, return the Job object."""

    existing_record = db.session.query(exists().where(Job.title == title)).scalar()

    if existing_record:
        return Job.query.filter(Job.title == title).first()
    else:
        job = add_job(title)
    return job


def get_film_by_moviedb_id(moviedb_id, play):
    """Given a film's MovieDB ID, return the Film object."""

    existing_record = db.session.query(exists().where(Film.moviedb_id == moviedb_id)).scalar()
    
    if existing_record:
        return Film.query.filter(Film.moviedb_id == moviedb_id).first()
    else:
        film = process_moviedb_film_details(moviedb_id, play)
        return film


def get_person_by_moviedb_id(moviedb_id):
    """Given a person's MovieDB ID, return (or create and return) a matching Person object."""

    existing_record = db.session.query(exists().where(Person.moviedb_id == moviedb_id)).scalar()

    if existing_record:
        return Person.query.filter(Person.moviedb_id == moviedb_id).first()
    else:
        person_profile = requests.get("https://api.themoviedb.org/3/person/" + str(moviedb_id) + "?api_key=" + MOVIEDB_API_KEY)
        person_profile = person_profile.json()
        imdb_id = person_profile["imdb_id"]
        full_name = person_profile["name"].split()
        fname, lname = full_name[0], full_name[-1]
        birthday = person_profile["birthday"]
        gender = person_profile["gender"]
        photo_path = person_profile["profile_path"]

        person = add_person(moviedb_id, imdb_id, fname, lname, birthday, gender, photo_path)
        return person


def get_play_by_shortname(shortname):
    """Given a play's shortname, return the play."""

    existing_record = db.session.query(exists().where(Play.shortname == shortname)).scalar()
    print(f"***************************** {existing_record}")
    if existing_record:
        return Play.query.filter(Play.shortname == shortname).one()
    else:
        play = add_play(plays[shortname], shortname)
        return play


def get_play_by_title(title):
    """Given a play's complete title, return the play."""

    existing_record = db.session.query(exists().where(Play.title == title)).scalar()

    if existing_record:
        return Play.query.filter(Play.title == title).first()
    else:
        add_play(title, plays[title])


def get_play_by_film(film):
    """Given a film, return the associated play."""

    play_id = film.play_id
    return Play.query.get(play_id).first()

# def get_hamlet_cast():
#     """Return all actor objects associated with Hamlet."""