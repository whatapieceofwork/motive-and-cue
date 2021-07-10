"""Create, Read, Update, Delete Operations. Listed alphabetically by section."""

from flask import Flask, render_template, redirect, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from bs4 import BeautifulSoup
from datetime import datetime
import jinja2
import os
import random
import requests
import re #regex
import json
from data_model import * 
# from folger_parser import parse_folger_characters, parse_folger_scenes
from folger_parser import *
from moviedb_parser import parse_moviedb_film_details
from forms import *

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()


play_titles = {"AWW": "All's Well That Ends Well", "Ant": "Antony and Cleopatra", "AYL": "As You Like It", "Err": "The Comedy of Errors", "Cor": "Coriolanus", "Cym": "Cymbeline", "Ham": "Hamlet", "1H4": "Henry IV, Part 1", "2H4": "Henry IV, Part 2", "H5": "Henry V", "1H6": "Henry VI, Part 1", "2H6": "Henry VI, Part 2", "3H6": "Henry VI, Part 3", "H8": "Henry VIII", "JC": "Julius Caesar", "Jn": "King John", "Lr": "King Lear", "LLL": "Love's Labor's Lost", "Mac": "Macbeth", "MM": "Measure for Measure", "MV": "The Merchant of Venice", "Wiv": "The Merry Wives of Windsor", "MND": "A Midsummer Night's Dream", "Ado": "Much Ado About Nothing", "Oth": "Othello", "Per": "Pericles", "R2": "Richard II", "R3": "Richard III", "Rom": "Romeo and Juliet", "Shr": "The Taming of the Shrew", "Tmp": "The Tempest", "Tim": "Timon of Athens", "Tit": "Titus Andronicus", "Tro": "Troilus and Cressida", "TN": "Twelfth Night", "TGV": "The Two Gentlemen of Verona", "TNK": "The Two Noble Kinsmen", "WT": "The Winter's Tale"}


# ----- BEGIN: AUTHORIZATION FUNCTIONS ----- #
# Functions related to user accounts and authentication.

def user_email_taken(email):
    """Check if an email is taken and returns True or False."""

    existing_email = db.session.query(exists().where(User.email == email)).scalar()
    
    return existing_email


def username_taken(username):
    """Check if a username is taken and returns True or False."""

    existing_username = db.session.query(exists().where(User.username == username)).scalar()
    
    return existing_username

# ----- END: AUTHORIZATION FUNCTIONS ----- #


# ----- BEGIN: ADD FUNCTIONS ----- #
# For creating new database records

def add_character(name, play, gender=None):
    """Create and return a new Character database record."""

    character = Character(name=name, gender=gender, play_id=play.id)

    db.session.add(character)
    db.session.commit()

    print(f"********* Created {character} *********")
    return character


def add_all_characters(play):
    """Given a play, create and return a group of new Character database records."""

    characters = parse_folger_characters(play)

    for character_name in characters:
        character = get_character(character_name, play)
        db.session.add(character)
    
    db.session.commit()

    return Character.query.filter(Character.play_id == play.id).all()


def add_choice(play, title, description):
    """Create and return a new Choice database record."""

    choice = Choice(play_id=play.id, title=title, description=description)

    db.session.add(choice)
    db.session.commit()

    print(f"********* Created {choice} *********")
    return choice


def add_choice_character(choice, character):
    """Create and return a new ChoiceCharacter database record."""

    choice_character = ChoiceCharacter(choice_id=choice.id, character_id=character.id)

    db.session.add(choice_character)
    db.session.commit()

    print(f"********* Created {choice_character} *********")
    return choice_character
    
    
def add_choice_scene(choice, scene):
    """Create and return a new ChoiceScene database record."""

    choice_scene = ChoiceScene(choice_id=choice.id, scene_id=scene.id)

    db.session.add(choice_scene)
    db.session.commit()

    print(f"********* Created {choice_scene} *********")
    return choice_scene


def add_film(play, moviedb_id, imdb_id, title, release_date, language, length, poster_path):
    """Create and return a new Film database record."""

    film = Film(play_id=play.id, moviedb_id=moviedb_id, imdb_id=imdb_id, title=title, release_date=release_date, language=language, length=length, poster_path=poster_path)

    db.session.add(film)
    db.session.commit()

    print(f"Created {film} *********")
    return film


def add_job(title):
    """Create and return a new Job database record."""

    job = Job(title=title)

    db.session.add(job)
    db.session.commit()

    print(f"********* Created {job} *********")
    return job


def add_job_held(film, job, person):
    """Create and return a new JobHeld database record."""

    jobheld = JobHeld(film_id=film.id, job_id=job.id, person_id=person.id)
    
    db.session.add(jobheld)
    db.session.commit()

    print(f"********* Created {jobheld} *********")
    return jobheld


def add_interpretation(choice, play, title, description, film, time_start, time_end):
    """Create and return a new Interpretation database record."""

    interpretation = Interpretation(choice_id=choice.id, play_id=play.id, film_id=film.id, title=title, description=description, time_start=time_start, time_end=time_end)

    db.session.add(interpretation)
    db.session.commit()

    print(f"********* Created {interpretation} *********")
    return interpretation


def add_interpretation_film(interpretation, film):
    """Create and return a new InterpretationFilm database record."""

    interpretation_film = InterpretationFilm(interpretation_id=interpretation.id, film_id=film.id)

    db.session.add(interpretation_film)
    db.session.commit()

    print(f"********* Created {interpretation_film} *********")
    return interpretation_film


def add_part_played(person, character_name, film):
    """Create and return a new PartPlayed database relationship record."""

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


def add_quote(play, character, scene, text):
    """Create and return a new Quote database record."""

    quote = Quote(play_id=play.id, character_id=character.id, scene_id=scene.id, text=text)
    db.session.add(quote)
    db.session.commit()


def add_scene(act, scene, play, title, description=None):
    """Create and return a new Scene database record."""

    scene = Scene(act=act, scene=scene, title=title, description=description, play_id=play.id)
    db.session.add(scene)
    db.session.commit()

    print(f"********* Created {scene} *********")
    return scene


def add_all_scenes(play):
    """Given a play, create and return new Scene database records."""

    scenes = parse_folger_scenes(play)
    print(f"****************** IN ADD_ALL_SCENES, play {play.title} *******************")
    print(f"****************** FOLGER SCENES: {scenes} *******************")


    for scene in scenes.values():
        db_scene = get_scene(act=scene["act"], scene=scene["scene"], play=play)
        db.session.add(db_scene)
    
    db.session.commit()

    return Scene.query.filter(Scene.play_id == play.id).all()


def add_topic(title, description):
    """Create and return a new Topic database record."""

    topic = Topic(title=title, description=description)

    db.session.add(topic)
    db.session.commit()

    print(f"********* Created {topic} *********")
    return topic

# ----- END: ADD FUNCTIONS ----- #


# ----- BEGIN: GET FUNCTIONS ----- #
# For retrieving existing database records or creating new ones

def get_character(name, play, gender=2):
    """Given a character name, gender, and play, return the Character object."""

    existing_character = db.session.query(exists().where((Character.name == name) & (Character.play_id == play.id))).scalar()
    
    if existing_character:
        character = Character.query.filter((Character.name == name) & (Character.play_id == play.id)).first()
    else:
        character = add_character(name=name, play=play, gender=gender)
    
    return character


def get_all_characters_by_play(play):
    """Given a play, return any existing related Character objects in the database."""

    existing_characters = db.session.query(exists().where(Character.play_id == play.id)).scalar()

    if existing_characters:
        characters = Character.query.filter(Character.play_id == play.id).order_by(Character.id).all()
    else:
        add_all_characters(play)
        characters = Character.query.filter(Character.play_id == play.id).order_by(Character.id).all()
    return characters


def get_choice(play, title):
    """Given a play and choice title, return the Choice database record."""

    existing_choice = db.session.query(exists().where((Choice.play_id == play.id) & (Choice.title == title))).scalar()

    if existing_choice:
        return Choice.query.filter((Choice.play_id == play.id) & (Choice.title == title)).first()
    else:
        return None


def get_all_choices_by_play(play):
    """Given a play, return any existing related Choice objects in the database."""

    existing_choices = db.session.query(exists().where(Choice.play_id == play.id)).scalar()

    if existing_choices:
        return Choice.query.filter(Choice.play_id == play.id).all()
    else:
        return None


def get_choice_character(choice, character):
    """Given a choice and character, return or create a ChoiceCharacter object."""

    existing_choice_character = db.session.query(exists().where((ChoiceCharacter.choice_id == choice.id) & (ChoiceCharacter.character_id == character.id))).scalar()

    if existing_choice_character:
        choice_character = ChoiceCharacter.query.filter((ChoiceCharacter.choice_id == choice.id) & (ChoiceCharacter.character_id == character.id)).first()
    else:
        choice_character = add_choice_character(choice, character)

    return choice_character


def get_choice_scene(choice, scene):
    """Given a choice and scene, return or create a ChoiceScene object."""

    existing_choice_scene = db.session.query(exists().where((ChoiceScene.choice_id == choice.id) & (ChoiceScene.scene_id == scene.id))).scalar()

    if existing_choice_scene:
        choice_scene = ChoiceScene.query.filter((ChoiceScene.choice_id == choice.id) & (ChoiceScene.scene_id == scene.id)).first()
    else:
        choice_scene = add_choice_scene(choice, scene)

    return choice_scene


def get_interpretation(choice, film):
    """Given a choice and film, return the related Interpretation object."""

    existing_interpretation = db.query.session(exists().where((Interpretation.choice_id == choice.id) & (Interpretation.film_id == film.id))).scalar()

    if existing_interpretation:
        return Interpretation.query.filter((Interpretation.choice_id == choice.id) & (Interpretation.film_id == film.id)).first()
    else:
        return None


def get_all_interpretations_by_play(play):
    """Given a play, return any existing related Interpretation objects in the database."""

    existing_interpretations = db.session.query(exists().where(Interpretation.play_id == play.id)).scalar()

    if existing_interpretations:
        return Interpretation.query.filter(Interpretation.play_id == play.id).all()
    else:
        return None


def get_interpretation_film(interpretation, film):
    """Given an interpreation and film, return the related InterpretationFilm object."""

    existing_interpretation_film = db.session.query(exists().where((InterpretationFilm.interpretation_id == interpretation.id) & (InterpretationFilm.film_id == film.id))).scalar()
    
    if existing_interpretation_film:
        interpretation_film = InterpretationFilm.query.filter((InterpretationFilm.interpretation_id == interpretation.id) & (InterpretationFilm.film_id == film.id)).first()
    else:
        interpretation_film = add_interpretation_film(interpretation, film)

    return interpretation_film


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


def get_films_by_play(play):
    """Given a play, return the related Film objects."""

    existing_films = db.session.query(exists().where(Film.play_id == play.id)).scalar()
    
    if existing_films:
        return Film.query.filter(Film.play_id == play.id).all()
    else:
        return None


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
        return play
    elif play_titles.get(shortname):
        play = add_play(play_titles[shortname], shortname)
        return play
    else:
        return None


def get_play_by_title(title):
    """Given a play's complete title, return the play."""

    existing_play = db.session.query(exists().where(Play.title == title)).scalar()

    if existing_play:
        play = Play.query.filter(Play.title == title).first()
    else:
        for shortname, play_title in play_titles.items():
            if title == play_title:
                play = add_play(shortname, play_title)
    
    return play


def get_play_by_film(film):
    """Given a film, return the associated play."""

    play_id = film.play_id
    play = Play.query.filter(Play.id == play_id).first()
    return play


def get_scene(act, scene, play, title=None, description=None):
    """Given an act, scene, and play, return the appropriate Scene object."""

    existing_scene = db.session.query(exists().where((Scene.act == act) & (Scene.scene == scene) & (Scene.play_id == play.id))).scalar()

    if existing_scene:
        scene = Scene.query.filter((Scene.act == act) & (Scene.scene == scene) & (Scene.play_id == play.id)).first()
        if title != scene.title or description != scene.description:
            updated_scene = update_scene(scene, title, description)
            return updated_scene
        else:
            return scene
    else:
        new_scene = add_scene(act=act, scene=scene, play=play, title=title, description=description)
        return new_scene


def get_all_scenes_by_play(play):
    """Given a play, return any existing related Scene objects in the database in order of act/scene."""

    existing_scenes = db.session.query(exists().where(Scene.play_id == play.id)).scalar()
    print(f"****************** IN GET_ALL_SCENES, play {play.title} *******************")
    print(f"****************** EXISTING SCENES: {existing_scenes} *******************")

    if existing_scenes:
        scenes = Scene.query.filter(Scene.play_id == play.id).order_by(Scene.act, Scene.scene).all()
    else:
        add_all_scenes(play)
        scenes = Scene.query.filter(Scene.play_id == play.id).order_by(Scene.act, Scene.scene).all()

    return scenes

# ----- END: GET FUNCTIONS ----- #


# ----- BEGIN: UPDATE FUNCTIONS ----- #
# For updating existing database records

def update_character(character, name=None, gender=None):
    """Given a character, update the existing values."""

    db_character = Character.query.get(character.id)

    if name != None:
        db_character.name = name
    if gender != None:
        db_character.gender = gender
    
    db.session.merge(db_character)
    db.session.commit()
    return db_character


def update_choice(choice, title=None, description=None):
    """Given a choice, update the existing values."""

    db_choice = Choice.query.get(choice.id)

    if title != None:
        db_choice.title = title
    if description != None:
        db_choice.description = description
    
    db.session.merge(db_choice)
    db.session.commit()
    return db_choice


def update_interpretation(interpretation, play=None, film=None, title=None, description=None, time_start=None, time_end=None):
    """Given an interpretation, update the existing values."""

    db_interpretation = Interpretation.query.get(interpretation.id)

    if play != None:
        db_interpretation.play = play
    if title != None:
        db_interpretation.title = title
    if film!= None:
        db_interpretation.film_id = film.id
    if description != None:
        db_interpretation.description = description
    if time_start != None:
        db_interpretation.time_start = time_start
    if time_end != None:
        db_interpretation.time_end = time_end
    
    db.session.merge(db_interpretation)
    db.session.commit()
    return db_interpretation


def update_scene(scene, title=None, description=None):
    """Given a scene, update the existing values."""

    db_scene = Scene.query.get(scene.id)

    if title != None:
        db_scene.title = title
    if description != None:
        db_scene.description = description
    
    db.session.merge(db_scene)
    db.session.commit()
    return db_scene

# ----- END: UPDATE FUNCTIONS ----- #


# ----- BEGIN: RANDOM FUNCTIONS ----- #
# For returning randomly selected records

def random_scene(play=None):
    """Returns a random scene. Can  be limited by play"""

    if play:
        scenes = Scene.query.filter(Scene.play_id == play.id).all()
    else:
        scenes = Scene.query.all()

    return random.choice(scenes)


# ----- BEGIN: RANDOM FUNCTIONS ----- #


# ----- BEGIN: MISC FUNCTIONS ----- #

def calculate_age_during_film(person, film):
    """Given a person and film, calculate the person's age when the film was released."""

    film_release = film.release_date
    birthday = person.birthday
    days_between = film_release - birthday
    age = int(days_between/365)

    return age

def seed_play(play):
    scenes = get_all_scenes_by_play(play)
    characters = get_all_characters_by_play(play)

# ----- END: MISC FUNCTIONS ----- #
