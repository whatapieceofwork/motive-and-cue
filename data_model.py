"""Data model."""

from flask import Flask, render_template, redirect, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from bs4 import BeautifulSoup
from datetime import datetime
import json
from crud import *
from server import plays

db = SQLAlchemy()

class Play(db.Model):
    """A single play."""

    __tablename__ = "plays"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50))
    shortname = db.Column(db.String(10))
    characters = db.relationship('Character')
    scenes = db.relationship('Scene')

    def __repr__(self):
        return f"<PLAY id={self.id} {self.title}>"


class Character(db.Model):
    """A character from the play."""

    __tablename__ = "characters"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship('Play')

    def __repr__(self):
        return f"<CHARACTER id={self.id} {self.name} {self.play_id}>"


class Scene(db.Model):
    """A scene from the play."""

    __tablename__ = "scenes"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    act = db.Column(db.Integer, nullable=False)
    scene = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100))
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play")

    def __repr__(self):
        return f"<SCENE id={self.scene} {self.act}.{self.scene}>"


class Person(db.Model):
    """A single person. May have multiple jobs and parts across multiple films."""

    __tablename__ = "people"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    moviedb_id = db.Column(db.Integer)
    imdb_id = db.Column(db.String)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))
    birthday = db.Column(db.Date)
    gender = db.Column(db.String(10))
    photo_path = db.Column(db.String(100))
    jobs = db.relationship('JobHeld', backref="people")
    parts = db.relationship('PartPlayed', backref="parts")

    def __repr__(self):
        return f"<PERSON id={self.id} {self.fname} {self.lname}>"


class Film(db.Model):
    """A film adaptation."""

    __tablename__ = "films"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    moviedb_id = db.Column(db.Integer)
    imdb_id = db.Column(db.String)
    title = db.Column(db.String(50), nullable=False, default="English")
    language = db.Column(db.String(15), nullable=False, default="English")
    length = db.Column(db.Integer)
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play")
    poster_path = db.Column(db.String(100))
    release_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<FILM id={self.id} {self.title} {self.release_date}>"


class Job(db.Model):
    """A role a person might play in a film: actor, director, etc. People can have many jobs."""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    # job_havers = relationship

    def __repr__(self):
        return f"<JOB id={self.id} {self.title}>"


class ChoicePoint(db.Model):
    """A point in the play where multiple interpretations could be made."""

    __tablename__ = "choicepoints"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text)
    # choicescenes - relationship
    # choicechars - relationship

    def __repr__(self):
        return f"<CHOICEPOINT id={self.id} {self.title}>"


class Interpretation(db.Model):
    """A film's specific interpretation of a choice point."""

    __tablename__ = "interpretations"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100))
    desc = db.Column(db.Text)

    def __repr__(self):
        return f"<INTERPRETATION id={self.id} {self.title}>"


# -- END Primary data objects --

# -- BEGIN Relationship objects --

class JobHeld(db.Model):
    """Relationships between people and the film jobs they've held."""

    __tablename__ = "jobs_held"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"))

    def __repr__(self):
        return f"<JOBHELD id={self.id} {self.person_id} {self.job_id}>"


class InterpretationFilms(db.Model):
    """Relationships between interpretations and films. Interpretations may be used by multiple films.."""

    __tablename__ = "interpretation_films"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    interpretation_id = (db.Integer, db.ForeignKey("interpretations.id"))
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"))


class PartPlayed(db.Model):
    """Relationships between actors and the parts they've played."""

    __tablename__ = "parts_played"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"))
    person = db.relationship("Person")
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))
    character = db.relationship("Character")
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
    film = db.relationship("Film")
    # play = db.relationship("Play",
    #     secondary="join(Film, PartPlayed, Film.id==PartPlayed.ilm_id)."
    #                     "join(Character, PartPlayed.character_id == Character.id)",
    #     primaryjoin="and_(Character.play_id == Play.id)",
    #                 uselist = False)

    def __repr__(self):
        return f"<PARTPLAYED id={self.id} {self.person_id} {self.character_id}>"


class Topic(db.Model):
    """Topic categories for choice points, ex: Madness, Casting."""

    __tablename__ = "topics"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text)
    quote = db.Column(db.Text)
    # topic_scene = relationship
    # topic_character = oh god I need another relationship table for this

    def __repr__(self):
        return f"<TOPIC id={self.topic_id} {self.title}>"


class TopicScene(db.Model):
    """Relationships between topics and scenes."""

    __tablename__ = "topic_scenes"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))

    def __repr__(self):
            return f"<TOPICSCENE id={self.id} {self.scene_id} {self.topic_id}>"


class TopicCharacter(db.Model):
    """Relationships between topics and characters."""

    __tablename__ = "topic_characters"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))

    def __repr__(self):
            return f"<TOPICCHARACTER id={self.id} {self.topic_id} {self.character_id}>"


class ChoiceScene(db.Model):
    """Relationships between choices and scenes."""

    __tablename__ = "choice_scenes"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("choicepoints.id"))
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))


    def __repr__(self):
            return f"<TOPICSCENE id={self.id} {self.choice_id} {self.scene_id}>"


class ChoiceCharacter(db.Model):
    """Relationships between choices and characters."""

    __tablename__ = "choice_characters"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("choicepoints.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))

    def __repr__(self):
            return f"<TOPICCHARACTER id={self.id} {self.choice_id} {self.character_id}>"

# -- END Relationship objects --


def connect_to_db(flask_app, db_uri='postgresql:///motiveandcuedb', echo=True):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri #URI: Uniform Resource Identify-er
    flask_app.config['SQLALCHEMY_ECHO'] = echo #Gives output for us to look at (that the computer is doing/has done)
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #this is sometimes buggy when true

    db.app = flask_app
    db.init_app(flask_app)

    print('Connected to the db!')


if __name__ == '__main__':
    from server import app
    connect_to_db(app)

    # os.system('dropdb motiveandcuedb')
    # print("Table dropped.")
    # os.system('createdb motiveandcuedb')
    # print("Table created.")
    db.create_all()

