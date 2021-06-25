"""Data model."""

from flask import Flask, render_template, redirect, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from sqlalchemy import *
from datetime import datetime
from server import *
from werkzeug.security import generate_password_hash, check_password_hash

# from server import play_titles

db = SQLAlchemy()

# -- BEGIN User authentication objects --

class User(UserMixin, db.Model):
    """A user on the Motive and Cue website."""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(70), unique=True, index=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    # roles = db.relationship("Role", back_populates="users")

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<USER id={self.id} {self.name}>"


class Role(db.Model):
    """User roles on the Motive and Cue website."""

    __tablename__ = "roles"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    # users = db.relationship("User", back_populates="roles")

    def __repr__(self):
        return f"<USER id={self.id} {self.name}>"

# -- END User authentication objects --


# -- BEGIN Primary data objects --

class Job(db.Model):
    """A role a person might play in a film: actor, director, etc. People can have many jobs."""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    people = db.relationship("Person", secondary="jobs_held", back_populates="jobs")
    jobs_held = db.relationship("JobHeld", back_populates="job")

    def __repr__(self):
        return f"<JOB id={self.id} {self.title}>"
            

class Play(db.Model):
    """A single play."""

    __tablename__ = "plays"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50))
    shortname = db.Column(db.String(10))
    characters = db.relationship("Character", back_populates="play")
    scenes = db.relationship("Scene", back_populates="play")
    films = db.relationship("Film", back_populates="plays")

    def __repr__(self):
        return f"<PLAY id={self.id} {self.title}>"


class Character(db.Model):
    """A character from the play."""

    __tablename__ = "characters"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    gender = db.Column(db.String(10))
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play", back_populates="characters")
    played_by = db.relationship("Person", secondary="parts_played", back_populates="parts")
    choices = db.relationship("Choice", secondary="choice_characters", back_populates="characters")
    topics = db.relationship("Topic", secondary="topic_characters", back_populates="characters")


    def __repr__(self):
        return f"<CHARACTER id={self.id} {self.name} {self.play_id}>"


class Scene(db.Model):
    """A scene from the play."""

    __tablename__ = "scenes"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    act = db.Column(db.Integer, nullable=False)
    scene = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    quote = db.Column(db.Text)
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play", back_populates="scenes")
    choices = db.relationship("Choice", secondary="choice_scenes", back_populates="scenes")
    topics = db.relationship("Topic", secondary="topic_scenes", back_populates="scenes")


    def __repr__(self):
        return f"<SCENE id={self.id} {self.act}.{self.scene} {self.play.title}>"


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
    jobs = db.relationship("Job", secondary="jobs_held", back_populates="people")
    jobs_held = db.relationship("JobHeld", back_populates="people")
    parts = db.relationship("Character", secondary="parts_played", back_populates="played_by")
    parts_played = db.relationship("PartPlayed", back_populates="person")
    films = db.relationship("Film", secondary="jobs_held", back_populates="actors")

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
    poster_path = db.Column(db.String(100))
    release_date = db.Column(db.Date, nullable=False)
    actors = db.relationship("Person", secondary="parts_played", back_populates="films")
    plays = db.relationship("Play", back_populates="films")
    jobs_held = db.relationship("JobHeld", back_populates="film")

    def __repr__(self):
        return f"<FILM id={self.id} {self.title} {self.release_date}>"


class Choice(db.Model):
    """A point in the play where multiple interpretations could be made."""

    __tablename__ = "choices"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text)
    quote = db.Column(db.Text)
    scenes = db.relationship("Scene", secondary="choice_scenes", back_populates="choices")
    characters = db.relationship("Character", secondary="choice_characters", back_populates="choices")

    def __repr__(self):
        return f"<CHOICE id={self.id} {self.title}>"


class Interpretation(db.Model):
    """A film's specific interpretation of a choice point."""

    __tablename__ = "interpretations"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100))
    time_start = db.Column(db.Integer)
    time_end = db.Column(db.Integer)
    desc = db.Column(db.Text)
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
    choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))

    def __repr__(self):
        return f"<INTERPRETATION id={self.id} {self.title}>"

# -- END Primary data objects --


# -- BEGIN Relationship objects --

class JobHeld(db.Model):
    """Relationships between people and the film jobs they've held."""

    __tablename__ = "jobs_held"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
    film = db.relationship("Film", back_populates="jobs_held")
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
    job = db.relationship("Job", back_populates="jobs_held")
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"))
    people = db.relationship("Person", back_populates="jobs_held")

    def __repr__(self):
        return f"<JOBHELD id={self.id} {self.job.title} {self.film.title}>"


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
    person = db.relationship("Person", back_populates="parts_played")
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))
    character = db.relationship("Character")
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
    film = db.relationship("Film")

    def __repr__(self):
        return f"<PARTPLAYED id={self.id} {self.person.lname} {self.character.name} {self.film.title}>"


class Topic(db.Model):
    """Topic categories for choice points, ex: Madness, Casting."""

    __tablename__ = "topics"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text)
    quote = db.Column(db.Text)
    scenes = db.relationship("Scene", secondary="topic_scenes", back_populates="topics")
    characters = db.relationship("Character", secondary="topic_characters", back_populates="topics")

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
    choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))


    def __repr__(self):
            return f"<CHOICESCENE id={self.id} {self.choice_id} {self.scene_id}>"


class ChoiceCharacter(db.Model):
    """Relationships between choices and characters."""

    __tablename__ = "choice_characters"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))

    def __repr__(self):
            return f"<CHOICECHARACTER id={self.id} {self.choice_id} {self.character_id}>"

# -- END Relationship objects --



def connect_to_db(flask_app, db_uri="postgresql:///motiveandcuedb", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri #URI: Uniform Resource Identify-er
    flask_app.config["SQLALCHEMY_ECHO"] = echo #Gives output for us to look at (that the computer is doing/has done)
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #this is sometimes buggy when true

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app
    connect_to_db(app)

    # os.system("dropdb motiveandcuedb")
    # print("Table dropped.")
    # os.system("createdb motiveandcuedb")
    # print("Table created.")
    db.create_all()

