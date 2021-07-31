# """Data model."""

# from app.search import add_to_index, remove_from_index, query_index
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import AnonymousUserMixin, UserMixin, login_manager
from flask_whooshee import AbstractWhoosheer, Whooshee
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import backref, relationship, reconstructor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

db = SQLAlchemy()
whooshee = Whooshee()


# ----- BEGIN DATA RELATIONSHIP MODELS ----- #

class CharacterActor(db.Model):
    """Relationship between a character and a person cast to play them."""

    __tablename__ = "character_actors"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"))
    person = db.relationship("Person", back_populates="character_actors")
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))
    character = db.relationship("Character")
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
    film = db.relationship("Film")

    def __repr__(self):
        return f"<CHARACTERACTOR id={self.id} {self.person.lname} {self.character.name} {self.film.title}>"

    def __str__(self):
        return f"{self.person.fname} {self.person.lname}, {self.character.name}"

    def age_during_film(self):
        age = calculate_age_during_film(self.person, self.film)
        return age


class CharacterInterpretation(db.Model): 
    """Relationships between a character and a film interpretation."""

    __tablename__ = "character_interpretations"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))
    interpretation_id = db.Column(db.Integer, db.ForeignKey("interpretations.id"))

    def __repr__(self):
            return f"<CHARACTERINTERPRETATION id={self.id} {self.character_id} {self.scene_id}>"


class CharacterQuestion(db.Model):
    """Relationship between a character and a textual question."""

    __tablename__ = "character_questions"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), primary_key=True)

    def __repr__(self):
            return f"<CHARACTERQUESTION id={self.id} {self.character_id} {self.scene_id}>"


class CharacterQuote(db.Model): 
    """Relationship between a character and quote."""

    __tablename__ = "character_quotes"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey("quotes.id"), primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"), primary_key=True)

    def __repr__(self):
            return f"<CHARACTERQUOTE id={self.id} {self.character_id} {self.scene_id}>"

            
class CharacterScene(db.Model): 
    """Relationship between a character and scene."""

    __tablename__ = "character_scenes"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"), primary_key=True)

    def __repr__(self):
            return f"<CHARACTERSCENE id={self.id} {self.character_id} {self.scene_id}>"


class CharacterTopic(db.Model):
    """Relationships between a character and a topic."""

    __tablename__ = "character_topics"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), primary_key=True)

    def __repr__(self):
            return f"<CHARACTERTOPIC id={self.id} {self.topic_id} {self.character_id}>"


class PersonJob(db.Model):
    """Relationship between a person and a film job."""

    __tablename__ = "person_jobs"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"), primary_key=True)
    film = db.relationship("Film", back_populates="person_jobs")
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), primary_key=True)
    job = db.relationship("Job", back_populates="person_jobs")
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"), primary_key=True)
    people = db.relationship("Person", back_populates="person_jobs")

    def __repr__(self):
        return f"<PERSONJOB id={self.id} {self.job.title} {self.film.title}>"

    def __str__(self):
        return f"{self.job.title}, {self.film.title}"


class SceneInterpretation(db.Model): 
    """Relationship between a scene and a film interpretation."""

    __tablename__ = "scene_interpretations"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"), primary_key=True)
    interpretation_id = db.Column(db.Integer, db.ForeignKey("interpretations.id"), primary_key=True)

    def __repr__(self):
            return f"<SCENEINTERPRETATION id={self.id} {self.question_id} {self.scene_id}>"


class SceneQuestion(db.Model): 
    """Relationship between a scene and a textual question."""

    __tablename__ = "scene_questions"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), primary_key=True)

    def __repr__(self):
            return f"<SCENEQUESTION id={self.id} {self.question_id} {self.scene_id}>"


class SceneTopic(db.Model):
    """Relationships a scene and a topic."""

    __tablename__ = "scene_topics"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), primary_key=True)

    def __repr__(self):
            return f"<SCENETOPIC id={self.id} {self.scene_id} {self.topic_id}>"


# ----- BEGIN PRIMARY DATA MODELS ----- #

GENDERS = {
    2: "Male",
    1: "Female",
    0: "Other/NA"
}

@whooshee.register_model("name")
class Character(db.Model):
    """A character from the play."""

    __tablename__ = "characters"
    __searchable__ = ["name"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    word_count = db.Column(db.Integer)
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play", back_populates="characters")
    played_by = db.relationship("Person", secondary="character_actors", foreign_keys=[CharacterActor.character_id, CharacterActor.person_id], backref="characters", lazy="dynamic")
    questions = db.relationship("Question", secondary="character_questions", foreign_keys=[CharacterQuestion.character_id, CharacterQuestion.question_id], backref="characters", lazy="dynamic", cascade="all")
    interpretations = db.relationship("Interpretation", secondary="character_interpretations", foreign_keys=[CharacterInterpretation.character_id, CharacterInterpretation.interpretation_id], backref="characters", lazy="dynamic", cascade="all")
    scenes = db.relationship("Scene", secondary="character_scenes", foreign_keys=[CharacterScene.character_id, CharacterScene.scene_id], backref="characters", lazy="dynamic", cascade="all")
    topics = db.relationship("Topic", secondary="character_topics", foreign_keys=[CharacterTopic.character_id, CharacterTopic.topic_id], backref="characters", lazy="dynamic", cascade="all")
    quotes = db.relationship("Quote", secondary="character_quotes", foreign_keys=[CharacterQuote.character_id, CharacterQuote.quote_id], backref="character", lazy="dynamic", cascade="all")

    def __repr__(self):
        return f"<CHARACTER id={self.id} {self.name} ({self.play.title})>"

    def __str__(self):
        return f"{self.name} ({self.play})"

@whooshee.register_model("moviedb_id", "imdb_id", "title", "release_date")
class Film(db.Model):
    """A film adaptation."""

    __tablename__ = "films"
    __searchable__ = ["moviedb_id", "imdb_id", "title", "release_date"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    moviedb_id = db.Column(db.Integer)
    imdb_id = db.Column(db.String)
    title = db.Column(db.String(50), nullable=False, default="English")
    language = db.Column(db.String(15), nullable=False, default="English")
    length = db.Column(db.Integer)
    overview = db.Column(db.Text)
    tagline = db.Column(db.Text)
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    poster_path = db.Column(db.String(100))
    release_date = db.Column(db.Date, nullable=False)
    actors = db.relationship("Person", secondary="character_actors", back_populates="films")
    play = db.relationship("Play", back_populates="films")
    person_jobs = db.relationship("PersonJob", back_populates="film")
    interpretations = db.relationship("Interpretation", back_populates="film")

    def __repr__(self):
        return f"<FILM id={self.id} {self.title} {self.release_date}>"

    def __str__(self):
        return f"{self.title}, {self.release_date}"


@whooshee.register_model("title", "description")
class Interpretation(db.Model):
    """A film's specific interpretation of a question point."""

    __tablename__ = "interpretations"
    __searchable__ = ["title", "description"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, info={"label": "ID"})
    title = db.Column(db.String(100), info={"label": "Title"})
    time_start = db.Column(db.Integer, info={"label": "Starting Timestamp"})
    time_end = db.Column(db.Integer, info={"label": "Ending Timestamp"})
    description = db.Column(db.Text, info={"label": "Description"})
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play", back_populates="interpretations")
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
    film = db.relationship("Film", back_populates="interpretations")
    # characters = db.relationship("Character", secondary="character_interpretations", back_populates="interpretations")
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), info={"label": "Question ID"})
    question = db.relationship("Question", info={"label": "Question"})
    scenes = db.relationship("Scene", secondary="scene_interpretations", foreign_keys=[SceneInterpretation.interpretation_id, SceneInterpretation.scene_id], info={"label": "Scenes"})


    def __repr__(self):
        return f"<INTERPRETATION id={self.id} {self.title}>"

    def __str__(self):
        return f"{self.title} ({self.play.title})"


@whooshee.register_model("title")
class Job(db.Model):
    """A role a person might serve in a film: actor, director, etc. One person can have many jobs."""

    __tablename__ = "jobs"
    __searchable__ = ["title"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    people = db.relationship("Person", secondary="person_jobs", back_populates="jobs")
    person_jobs = db.relationship("PersonJob", back_populates="job")

    def __repr__(self):
        return f"<JOB id={self.id} {self.title}>"

    def __str__(self):
        return f"{self.title}"


@whooshee.register_model("fname", "lname", "moviedb_id", "imdb_id")
class Person(db.Model):
    """A single person. May have multiple jobs and parts across multiple films."""

    __tablename__ = "people"
    __searchable__ = ["fname", "lname", "moviedb_id", "imdb_id"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    moviedb_id = db.Column(db.Integer)
    imdb_id = db.Column(db.String)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))
    birthday = db.Column(db.Date)
    gender = db.Column(db.String(10))
    photo_path = db.Column(db.String(100))
    jobs = db.relationship("Job", secondary="person_jobs", back_populates="people")
    person_jobs = db.relationship("PersonJob", back_populates="people")
    parts = db.relationship("Character", secondary="character_actors", back_populates="played_by", cascade="all")
    character_actors = db.relationship("CharacterActor", back_populates="person")
    films = db.relationship("Film", secondary="person_jobs", back_populates="actors")

    def __repr__(self):
        return f"<PERSON id={self.id} {self.fname} {self.lname}>"

    def __str__(self):
        return f"{self.fname} {self.lname}"


@whooshee.register_model("title")
class Play(db.Model):
    """A single play."""

    __tablename__ = "plays"
    __searchable__ = ["title"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50))
    shortname = db.Column(db.String(10))
    characters = db.relationship("Character", back_populates="play")
    questions = db.relationship("Question", back_populates="play")
    scenes = db.relationship("Scene", back_populates="play")
    films = db.relationship("Film", back_populates="play")
    quotes = db.relationship("Quote", back_populates="play")
    interpretations = db.relationship("Interpretation", back_populates="play")

    def __repr__(self):
        return f"<PLAY id={self.id} {self.title}>"

    def __str__(self):
        return f"{self.title}"


@whooshee.register_model("title", "description")
class Question(db.Model):
    """A textual question in the play where multiple interpretations could be made."""

    __tablename__ = "questions"
    __searchable__ = ["title", "description"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, info={"label": "ID"})
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play", back_populates="questions")
    title = db.Column(db.String(50), nullable=False, info={"label": "Title"})
    description = db.Column(db.Text, info={"label": "Description"})
    # scenes = db.relationship("Scene", secondary="scene_questions", back_populates="questions")
    # characters = db.relationship("Character", secondary="character_questions", back_populates="questions")
    interpretations = db.relationship("Interpretation", back_populates="question")
    # url = db.Column(db.String(500))

    # @reconstructor
    # def init_on_load(self):
    #     self.url = f"/{self.__tablename__}/{self.id}"

    def __repr__(self):
        return f"<CHOICE id={self.id} {self.title}>"


@whooshee.register_model("title", "description")
class Scene(db.Model):
    """A scene from the play."""

    __tablename__ = "scenes"
    __searchable__ = ["title", "description"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    act = db.Column(db.Integer, nullable=False)
    scene = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String)
    description = db.Column(db.Text)
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play", back_populates="scenes")
    questions = db.relationship("Question", secondary="scene_questions", foreign_keys=[SceneQuestion.scene_id, SceneQuestion.question_id], backref="scenes", lazy="dynamic", cascade="all")
    interpretations = db.relationship("Interpretation", secondary="scene_interpretations", foreign_keys=[SceneInterpretation.scene_id, SceneInterpretation.interpretation_id], back_populates="scenes", lazy="dynamic", cascade="all")
    topics = db.relationship("Topic", secondary="scene_topics", foreign_keys=[SceneTopic.scene_id, SceneTopic.topic_id], backref="scenes", lazy="dynamic", cascade="all")
    quotes = db.relationship("Quote", back_populates="scene")
    
    def __repr__(self):
        return f"<SCENE id={self.id} {self.act}.{self.scene} {self.play.title}>"

    def __str__(self):
        if self.title:
            return f"{self.play.title} ({self.act}.{self.scene}): {self.title}"
        else:
            return f"{self.play.title} ({self.act}.{self.scene})"


class Topic(db.Model):
    """Topic categories for question points, ex: Madness, Casting."""

    __tablename__ = "topics"
    __searchable__ = ["title", "description"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    # scenes = db.relationship("Scene", secondary="scene_topics", back_populates="topics")
    # characters = db.relationship("Character", secondary="character_topics", back_populates="topics")

    def __repr__(self):
        return f"<TOPIC id={self.topic_id} {self.title}>"

    def __str__(self):
        return f"{self.title}"


class Quote(db.Model):
    """A quote from a play."""

    __tablename__ = "quotes"
    __searchable__ = ["text"]

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    text = db.Column(db.Text)
    play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
    play = db.relationship("Play", back_populates="quotes")
    # character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))
    # character = db.relationship("Character", back_populates="quotes")
    scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))
    scene = db.relationship("Scene", back_populates="quotes")

    def __repr__(self):
        return f"<QUOTE id={self.id} {self.character.name}>"

    def __str__(self):
        return f"'{self.text}' {self.character.name} ({self.play.title} ({self.scene.act}.{self.scene.scene}))"


# -- END Primary data objects --


# ----- BEGIN USER AUTHENTICATION MODELS ----- #

class User(UserMixin, db.Model):
    """A user on the Motive and Cue website."""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(70), unique=True, index=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(150))
    about = db.Column(db.Text())
    password_hash = db.Column(db.String(10000))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["HEAD_ADMIN"]:
                self.role = Role.query.filter_by(name="Admin").first()
                print(f"Set {self}'s role as Admin")
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
                print(f"Set {self}'s role as {self.role}")
                

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, expiration=3600):
        serializer = Serializer(current_app.config["SECRET_KEY"], expiration)
        return serializer.dumps({"confirm": self.id}).decode("utf-8")

    def confirm_account_token(self, token):
        serializer = Serializer(current_app.config["SECRET_KEY"])

        try:
            data = serializer.loads(token.encode("utf-8"))
            print(f"In confirm, token = {token}")
        except:
            return False

        if data.get("confirm") != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        db.session.commit

        return True

    @staticmethod
    def confirm_reset_token(self, token):
        serializer = Serializer(current_app.config["SECRET_KEY"])

        try:
            data = serializer.loads(token.encode("utf-8"))
        except:
            return False

        id = data.get("confirm")
        return User.query.get(id)

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<USER id={self.id} {self.name}>"

    def __str__(self):
        # Used in WTF-Alchemy forms and on front-end
        return f"{self.username}"


class AnonymousUser(AnonymousUserMixin):
    """An anonymous user class used by Flask-Login."""
    def can(self, permissions):
        return False

    def is_admin(self):
        return False


class Role(db.Model):
    """User roles on the Motive and Cue website."""

    __tablename__ = "roles"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(300))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    @staticmethod
    def insert_roles():
        """Find and update existing roles. Create roles as necessary."""

        roles = {
            "User": [Permission.FOLLOW],
            "Contributor": [Permission.FOLLOW, Permission.SUGGEST_EDIT],
            "Editor": [Permission.FOLLOW, Permission.SUGGEST_EDIT, Permission.APPROVE_EDIT],
            "Creator": [Permission.FOLLOW, Permission.SUGGEST_EDIT, Permission.APPROVE_EDIT, Permission.ADD],
            "Admin": [Permission.FOLLOW, Permission.SUGGEST_EDIT, Permission.APPROVE_EDIT, Permission.ADD, Permission.ADMIN],
        }

        default_role = "User"
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None: # if role doesn't exist, create role
                role = Role(name=r)
            role.reset_permissions()
            for permission in roles[r]:
                role.add_permission(permission)
            role.default = (role.name == default_role)
            db.session.add(role)
            db.session.commit()

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm): # bitwise operator: check if combined permission value includes given permission
        return self.permissions & perm == perm

    def __repr__(self):
        return f"<ROLE id={self.id} {self.name}>"

    def __str__(self):
        return f"{self.name}"

class Permission:
    FOLLOW = 1
    SUGGEST_EDIT = 2
    APPROVE_EDIT = 4
    ADD = 8
    ADMIN = 32

# ----- END USER AUTHENTICATION MODELS ----- #