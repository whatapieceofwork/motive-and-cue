"""Data model."""

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

FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()

plays = {
	"Ham": "Hamlet",
}

# -- BEGIN Primary data objects --

class Play(db.Model):
    """A single play."""

    __tablename__ = "plays"

    play_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    title = db.Column(db.String(50),
                        )
    shortname = db.Column(db.String(10),
                        )

    def __repr__(self):
        return f"<PLAY id={self.play_id} {self.title}>"


class Character(db.Model):
    """A character from the play."""

    __tablename__ = "characters"

    character_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    name = db.Column(db.String(25),
                    nullable=False,
                    unique=True,
                    )
    play_id = db.Column(db.Integer,
                    db.ForeignKey("plays.play_id"),
                    )
    # actors = relationship

    def __repr__(self):
        return f"<CHARACTER id={self.character_id} {self.name} {self.play_id}>"

        
class ChoicePoint(db.Model):
    """A point in the play where multiple interpretations could be made."""

    __tablename__ = "choicepoints"

    choicepoint_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    title = db.Column(db.String(50),
                        nullable=False,
                        )
    desc = db.Column(db.Text
            )
    # choicescenes - relationship
    # choicechars - relationship

    def __repr__(self):
        return f"<CHOICEPOINT id={self.choicepoint_id} {self.title}>"


class Film(db.Model):
    """A film adaptation."""

    __tablename__ = "films"

    film_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    moviedb_id = db.Column(db.Integer,
                        )
    imdb_id = db.Column(db.String,
                        )
    title = db.Column(db.String(50),
                        nullable=False,
                        default="English",
                        )
    language = db.Column(db.String(15),
                        nullable=False,
                        default="English",
                        )
    length = db.Column(db.Integer,
                        )
    #person_id for director (FOREIGNKEY) (add to repr)
    play_id = db.Column(db.Integer,
                    db.ForeignKey("plays.play_id"),
                    )
    poster_path = db.Column(db.String(100),
                        )
    release_date = db.Column(db.Date,
                        nullable=False,
                        )

    def __repr__(self):
        return f"<FILM id={self.film_id} {self.title} {self.release_date}>"


class Interpretation(db.Model):
    """A film's specific interpretation of a choice point."""

    __tablename__ = "interpretations"

    interpretation_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    title = db.Column(db.String(100),
                    )
    desc = db.Column(db.Text,
                    )

    def __repr__(self):
        return f"<INTERPRETATION id={self.interpretation_id} {self.title} DIRECTORLNAME>"


class Job(db.Model):
    """A role a person might play in a film: actor, director, etc. People can have many jobs."""

    __tablename__ = "jobs"

    job_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    title = db.Column(db.String(50),
                    nullable=False,
                    unique=True,
                    )
    # job_havers = relationship

    def __repr__(self):
        return f"<JOB id={self.job_id} {self.title}>"


class Person(db.Model):
    """A single person. May have multiple jobs and parts across multiple films."""

    __tablename__ = "people"

    person_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    person_moviedb_id = db.Column(db.Integer,
                        )
    person_imdb_id = db.Column(db.String,
                        )
    fname = db.Column(db.String(30),
                        )
    lname = db.Column(db.String(30),
                        )
    birthday = db.Column(db.Date
                        )
    gender = db.Column(db.String(10)
                        )
    photo_path = db.Column(db.String(100)
                        )
    # roles = relationship
    # parts = relationship

    def __repr__(self):
        return f"<PERSON id={self.person_id} {self.fname} {self.lname}>"


class Scene(db.Model):
    """A scene from the play."""

    __tablename__ = "scenes"

    scene_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    title = db.Column(db.String(100),
                    )
    act_num = db.Column(db.Integer,
                    nullable=False,
                    )
    scene_num = db.Column(db.Integer,
                    nullable=False,
                    )

    def __repr__(self):
        return f"<SCENE id={self.scene_id} {self.act_num}.{self.scene_num}>"

# -- END Primary data objects --

# -- BEGIN Relationship objects --

class JobHeld(db.Model):
    """Relationships between people and the film jobs they've held."""

    __tablename__ = "jobs_held"

    jobheld_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    film_id = db.Column(db.Integer,
                    db.ForeignKey("films.film_id"),
                    )
    job_id = db.Column(db.Integer,
                    db.ForeignKey("jobs.job_id"),
                    )
    person_id = db.Column(db.Integer,
                    db.ForeignKey("people.person_id"),
                    )

    def __repr__(self):
        return f"<JOBHELD id={self.jobheld_id} {self.person_id} {self.job_id}>"


class InterpretationFilms(db.Model):
    """Relationships between interpretations and films. Interpretations may be used by multiple films.."""

    __tablename__ = "interpretation_films"
    interpretation_film = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    interpretation_id = (db.Integer,
                        db.ForeignKey("interpretations.interpretation_id"),
                        )
    film_id = db.Column(db.Integer,
                        db.ForeignKey("films.film_id"),
                        )


class PartPlayed(db.Model):
    """Relationships between actors and the parts they've played."""

    __tablename__ = "parts_played"

    partplayed_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    person_id = db.Column(db.Integer,
                    db.ForeignKey("people.person_id"),
                    )
    character_id = db.Column(db.Integer,
                    db.ForeignKey("characters.character_id"),
                    )
    film_id = db.Column(db.Integer,
                    db.ForeignKey("films.film_id"),
                    )

    def __repr__(self):
        return f"<PARTPLAYED id={self.partplayed_id} {self.person_id} {self.character_id}>"


class Topic(db.Model):
    """Topic categories for choice points, ex: Madness, Casting."""

    __tablename__ = "topics"

    topic_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    title = db.Column(db.String(100),
                    nullable=False,
                    )
    desc = db.Column(db.Text,
                    )
    quote = db.Column(db.Text,
                    )
    # topic_scene = relationship
    # topic_character = oh god I need another relationship table for this

    def __repr__(self):
        return f"<TOPIC id={self.topic_id} {self.title}>"


class TopicScene(db.Model):
    """Relationships between topics and scenes."""

    __tablename__ = "topic_scenes"

    topicscene_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    topic_id = db.Column(db.Integer,
                    db.ForeignKey("topics.topic_id"),
                    )
    scene_id = db.Column(db.Integer,
                db.ForeignKey("scenes.scene_id"),
                )

    def __repr__(self):
            return f"<TOPICSCENE id={self.topicscene_id} {self.scene_id} {self.topic_id.topic_title}>"


class TopicCharacter(db.Model):
    """Relationships between topics and characters."""

    __tablename__ = "topic_characters"

    topiccharacter_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    topic_id = db.Column(db.Integer,
                db.ForeignKey("topics.topic_id"),
                )
    character_id = db.Column(db.Integer,
                db.ForeignKey("characters.character_id"),
                )

    def __repr__(self):
            return f"<TOPICCHARACTER id={self.topiccharacter_id} {self.topic_id.topic_title} {self.character_id.name}>"


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
    
    os.system('dropdb motiveandcuedb')
    print("Table dropped.")
    os.system('createdb motiveandcuedb')
    print("Table created.")
    db.create_all()

