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
from folger_parser import *
from moviedb_parser import *

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()

plays = {"AWW": "All's Well That Ends Well", "Ant": "Antony and Cleopatra", "AYL": "As You Like It", "Err": "The Comedy of Errors", "Cor": "Coriolanus", "Cym": "Cymbeline", "Ham": "Hamlet", "1H4": "Henry IV, Part 1", "2H4": "Henry IV, Part 2", "H5": "Henry V", "1H6": "Henry VI, Part 1", "2H6": "Henry VI, Part 2", "3H6": "Henry VI, Part 3", "H8": "Henry VIII", "JC": "Julius Caesar", "Jn": "King John", "Lr": "King Lear", "LLL": "Love's Labor's Lost", "Mac": "Macbeth", "MM": "Measure for Measure", "MV": "The Merchant of Venice", "Wiv": "The Merry Wives of Windsor", "MND": "A Midsummer Night's Dream", "Ado": "Much Ado About Nothing", "Oth": "Othello", "Per": "Pericles", "R2": "Richard II", "R3": "Richard III", "Rom": "Romeo and Juliet", "Shr": "The Taming of the Shrew", "Tmp": "The Tempest", "Tim": "Timon of Athens", "Tit": "Titus Andronicus", "Tro": "Troilus and Cressida", "TN": "Twelfth Night", "TGV": "Two Gentlemen of Verona", "TNK": "Two Noble Kinsmen", "WT": "The Winter's Tale"}

def add_character(name, play, gender=None):
    """Create and return a new Character database record."""

    character = Character(name=name, gender=gender, play_id=play.id)

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


def add_part_played(person, character_name, film):
    """Create and return a PartPlayed database relationship record."""

    play = get_play_by_film(film)
    character = get_character(name=character_name, play=play)

    print(f"**** IN ADD_PART_PLAYED, play = {play}, person={person}, character_name={character_name}")

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


def get_character(name, play, gender=None):
    """Given a character name, gender, and play, return the Character object."""

    existing_character = db.session.query(exists().where((Character.name == name) & (Character.play_id == play.id))).scalar()
    
    if existing_character:
        character = Character.query.filter((Character.name == name) & (Character.play_id == play.id)).first()
    else:
        character = add_character(name=name, play=play, gender=gender)
    
    return character


def get_job_by_title(title):
    """Given a job title, return the Job object."""

    existing_job = db.session.query(exists().where(Job.title == title)).scalar()

    if existing_job:
        job = Job.query.filter(Job.title == title).first()
    else:
        job = add_job(title)
    
    return job


def get_job_held(person, film, job_title):
    """Given a person, film and job title, return (or create and return) a JobHeld object."""

    job = get_job_by_title(job_title)

    existing_job_held = db.session.query(exists().where((JobHeld.person_id == person.id) & (JobHeld.film_id == film.id) & (JobHeld.job_id == job.id))).scalar()
    
    if existing_job_held:
        job_held = JobHeld.query.filter((JobHeld.person_id == person.id) & (JobHeld.film_id == film.id) & (JobHeld.job_id == job.id)).first()
    else:
        job_held = add_job_held(film, job, person)
    
    return job_held


def get_film(play, moviedb_id, imdb_id, title, release_date, language, length, poster_path):

    existing_film = db.session.query(exists().where(Film.moviedb_id == moviedb_id)).scalar()
    
    if existing_film:
        film = Film.query.filter(Film.moviedb_id == moviedb_id).first()
    else:
        film = add_film(play, moviedb_id, imdb_id, title, release_date, language, length, poster_path)
    
    return film


def get_film_by_moviedb_id(moviedb_id, play):
    """Given a film's MovieDB ID, return the Film object."""

    existing_film = db.session.query(exists().where(Film.moviedb_id == moviedb_id)).scalar()
    
    if existing_film:
        film = Film.query.filter(Film.moviedb_id == moviedb_id).first()
    else:
        film = parse_moviedb_film_details(moviedb_id, play)
    
    return film


def get_person(moviedb_id, imdb_id, fname, lname, birthday, gender, photo_path):
    """Given a person's information, create (or return) a Person object."""

    existing_person = db.session.query(exists().where((Person.moviedb_id == moviedb_id) & (Person.fname == fname) & (Person.lname == lname))).scalar()

    if existing_person:
        person = Person.query.filter((Person.moviedb_id == moviedb_id) & (Person.fname == fname) & (Person.lname == lname)).first()
    else:
        person = add_person(moviedb_id=moviedb_id, imdb_id=imdb_id, fname=fname, lname=lname,
                    birthday=birthday, gender=gender, photo_path=photo_path)
    
    return person


def get_part_played(person, character_name, film):
    """Given a person's information, create (or return) a Person object."""

    play = get_play_by_film(film)
    character = get_character(character_name, play)

    existing_part_played = db.session.query(exists().where((PartPlayed.person_id == person.id) & (PartPlayed.character_id == character.id) & (PartPlayed.film_id == film.id))).scalar()

    if existing_part_played:
        part_played = PartPlayed.query.filter((PartPlayed.person_id == person.id) & (PartPlayed.character_id == character.id) & (PartPlayed.film_id == film.id)).first()
    else:
        part_played = add_part_played(person=person, character_name=character_name, film=film)
    
    return part_played


def get_play_by_shortname(shortname):
    """Given a play's shortname, return the play."""

    existing_play = db.session.query(exists().where(Play.shortname == shortname)).scalar()

    if existing_play:
        play = Play.query.filter(Play.shortname == shortname).one()
    else:
        play = add_play(plays[shortname], shortname)
    
    return play


def get_play_by_title(title):
    """Given a play's complete title, return the play."""

    existing_play = db.session.query(exists().where(Play.title == title)).scalar()

    if existing_play:
        play = Play.query.filter(Play.title == title).first()
    else:
        play = add_play(title, plays[title])
    
    return play


def get_play_by_film(film):
    """Given a film, return the associated play."""

    play_id = film.play_id
    play = Play.query.filter(Play.id == play_id).first()
    return play