# """Data model."""

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import AnonymousUserMixin, UserMixin, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import *
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """A user on the Motive and Cue website."""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(70), unique=True, index=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
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
    def password(self, password):
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

# -- END User authentication objects --


# # -- BEGIN Primary data objects --


# class Character(db.Model):
#     """A character from the play."""

#     __tablename__ = "characters"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     gender = db.Column(db.String(10))
#     word_count = db.Column(db.Integer)
#     play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
#     play = db.relationship("Play", back_populates="characters")
#     played_by = db.relationship("Person", secondary="parts_played", back_populates="parts")
#     choices = db.relationship("Choice", secondary="choice_characters", back_populates="characters")
#     interpretations = db.relationship("Interpretation", secondary="interpretation_characters", back_populates="characters")
#     scenes = db.relationship("Scene", secondary="character_scenes", back_populates="characters")
#     topics = db.relationship("Topic", secondary="topic_characters", back_populates="characters")
#     quotes = db.relationship("Quote", back_populates="character")

#     def __repr__(self):
#         return f"<CHARACTER id={self.id} {self.name} ({self.play.title})>"

#     def __str__(self):
#         return f"{self.name} ({self.play})"


# class Choice(db.Model):
#     """A point in the play where multiple interpretations could be made."""

#     __tablename__ = "choices"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True, info={"label": "ID"})
#     play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
#     play = db.relationship("Play", back_populates="choices")
#     title = db.Column(db.String(50), nullable=False, info={"label": "Title"})
#     description = db.Column(db.Text, info={"label": "Description"})
#     scenes = db.relationship("Scene", secondary="choice_scenes", back_populates="choices")
#     characters = db.relationship("Character", secondary="choice_characters", back_populates="choices")
#     interpretations = db.relationship("Interpretation", back_populates="choice")

#     def __repr__(self):
#         return f"<CHOICE id={self.id} {self.title}>"

#     def __str__(self):
#         return f"{self.title}"


# class Film(db.Model):
#     """A film adaptation."""

#     __tablename__ = "films"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     moviedb_id = db.Column(db.Integer)
#     imdb_id = db.Column(db.String)
#     title = db.Column(db.String(50), nullable=False, default="English")
#     language = db.Column(db.String(15), nullable=False, default="English")
#     length = db.Column(db.Integer)
#     play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
#     poster_path = db.Column(db.String(100))
#     release_date = db.Column(db.Date, nullable=False)
#     actors = db.relationship("Person", secondary="parts_played", back_populates="films")
#     play = db.relationship("Play", back_populates="films")
#     jobs_held = db.relationship("JobHeld", back_populates="film")
#     interpretations = db.relationship("Interpretation", back_populates="film")

#     def __repr__(self):
#         return f"<FILM id={self.id} {self.title} {self.release_date}>"

#     def __str__(self):
#         return f"{self.title}, {self.release_date}"


# class Interpretation(db.Model):
#     """A film's specific interpretation of a choice point."""

#     __tablename__ = "interpretations"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True, info={"label": "ID"})
#     title = db.Column(db.String(100), info={"label": "Title"})
#     time_start = db.Column(db.Integer, info={"label": "Starting Timestamp"})
#     time_end = db.Column(db.Integer, info={"label": "Ending Timestamp"})
#     description = db.Column(db.Text, info={"label": "Description"})
#     play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
#     play = db.relationship("Play", back_populates="interpretations")
#     film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
#     film = db.relationship("Film", back_populates="interpretations")
#     characters = db.relationship("Character", secondary="interpretation_characters", back_populates="interpretations")
#     choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"), info={"label": "Choice ID"})
#     choice = db.relationship("Choice", back_populates="interpretations", info={"label": "Choice"})
#     scenes = db.relationship("Scene", secondary="interpretation_scenes", back_populates="interpretations", info={"label": "Scenes"})


#     def __repr__(self):
#         return f"<INTERPRETATION id={self.id} {self.title}>"

#     def __str__(self):
#         return f"{self.title} ({self.play.title})"


# class Job(db.Model):
#     """A role a person might play in a film: actor, director, etc. People can have many jobs."""

#     __tablename__ = "jobs"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     title = db.Column(db.String(50), nullable=False, unique=True)
#     people = db.relationship("Person", secondary="jobs_held", back_populates="jobs")
#     jobs_held = db.relationship("JobHeld", back_populates="job")

#     def __repr__(self):
#         return f"<JOB id={self.id} {self.title}>"

#     def __str__(self):
#         return f"{self.title}"


# class Person(db.Model):
#     """A single person. May have multiple jobs and parts across multiple films."""

#     __tablename__ = "people"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     moviedb_id = db.Column(db.Integer)
#     imdb_id = db.Column(db.String)
#     fname = db.Column(db.String(30))
#     lname = db.Column(db.String(30))
#     birthday = db.Column(db.Date)
#     gender = db.Column(db.String(10))
#     photo_path = db.Column(db.String(100))
#     jobs = db.relationship("Job", secondary="jobs_held", back_populates="people")
#     jobs_held = db.relationship("JobHeld", back_populates="people")
#     parts = db.relationship("Character", secondary="parts_played", back_populates="played_by")
#     parts_played = db.relationship("PartPlayed", back_populates="person")
#     films = db.relationship("Film", secondary="jobs_held", back_populates="actors")

#     def __repr__(self):
#         return f"<PERSON id={self.id} {self.fname} {self.lname}>"

#     def __str__(self):
#         return f"{self.fname} {self.lname}"


# class Play(db.Model):
#     """A single play."""

#     __tablename__ = "plays"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     title = db.Column(db.String(50))
#     shortname = db.Column(db.String(10))
#     characters = db.relationship("Character", back_populates="play")
#     choices = db.relationship("Choice", back_populates="play")
#     scenes = db.relationship("Scene", back_populates="play")
#     films = db.relationship("Film", back_populates="play")
#     quotes = db.relationship("Quote", back_populates="play")
#     interpretations = db.relationship("Interpretation", back_populates="play")

#     def __repr__(self):
#         return f"<PLAY id={self.id} {self.title}>"

#     def __str__(self):
#         return f"{self.title}"


# class Scene(db.Model):
#     """A scene from the play."""

#     __tablename__ = "scenes"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     act = db.Column(db.Integer, nullable=False)
#     scene = db.Column(db.Integer, nullable=False)
#     title = db.Column(db.String)
#     description = db.Column(db.Text)
#     play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
#     play = db.relationship("Play", back_populates="scenes")
#     characters = db.relationship("Character", secondary="character_scenes", back_populates="scenes")
#     choices = db.relationship("Choice", secondary="choice_scenes", back_populates="scenes")
#     interpretations = db.relationship("Interpretation", secondary="interpretation_scenes", back_populates="scenes", info={"label": "Interpretations"})
#     quotes = db.relationship("Quote", back_populates="scene")
#     topics = db.relationship("Topic", secondary="topic_scenes", back_populates="scenes")

#     def __repr__(self):
#         return f"<SCENE id={self.id} {self.act}.{self.scene} {self.play.title}>"

#     def __str__(self):
#         if self.title:
#             return f"{self.play.title} ({self.act}.{self.scene}): {self.title}"
#         else:
#             return f"{self.play.title} ({self.act}.{self.scene})"


# class Topic(db.Model):
#     """Topic categories for choice points, ex: Madness, Casting."""

#     __tablename__ = "topics"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)
#     scenes = db.relationship("Scene", secondary="topic_scenes", back_populates="topics")
#     characters = db.relationship("Character", secondary="topic_characters", back_populates="topics")

#     def __repr__(self):
#         return f"<TOPIC id={self.topic_id} {self.title}>"

#     def __str__(self):
#         return f"{self.title}"


# class Quote(db.Model):
#     """A quote from a play."""

#     __tablename__ = "quotes"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     text = db.Column(db.Text)
#     play_id = db.Column(db.Integer, db.ForeignKey("plays.id"))
#     play = db.relationship("Play", back_populates="quotes")
#     character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))
#     character = db.relationship("Character", back_populates="quotes")
#     scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))
#     scene = db.relationship("Scene", back_populates="quotes")

#     def __repr__(self):
#         return f"<QUOTE id={self.id} {self.character.name}>"

#     def __str__(self):
#         return f"'{self.text}' {self.character.name} ({self.play.title} ({self.scene.act}.{self.scene.scene}))"


# # -- END Primary data objects --


# # -- BEGIN Relationship objects --

# class CharacterScene(db.Model): 
#     """Relationships between characters and scenes."""

#     __tablename__ = "character_scenes"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))
#     scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))

#     def __repr__(self):
#             return f"<CHARACTERSCENE id={self.id} {self.character_id} {self.scene_id}>"


# class ChoiceCharacter(db.Model):
#     """Relationships between choices and characters."""

#     __tablename__ = "choice_characters"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))
#     character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))

#     def __repr__(self):
#             return f"<CHOICECHARACTER id={self.id} {self.choice_id} {self.character_id}>"


# class ChoiceScene(db.Model): 
#     """Relationships between choices and scenes."""

#     __tablename__ = "choice_scenes"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))
#     scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))

#     def __repr__(self):
#             return f"<CHOICESCENE id={self.id} {self.choice_id} {self.scene_id}>"


# class InterpretationCharacter(db.Model): 
#     """Relationships between interpretations and characters."""

#     __tablename__ = "interpretation_characters"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     interpretation_id = db.Column(db.Integer, db.ForeignKey("interpretations.id"))
#     character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))

#     def __repr__(self):
#             return f"<INTERPRETATIONCHARACTER id={self.id} {self.character_id} {self.scene_id}>"


# class InterpretationScene(db.Model): 
#     """Relationships between interpretations and scenes."""

#     __tablename__ = "interpretation_scenes"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     interpretation_id = db.Column(db.Integer, db.ForeignKey("interpretations.id"))
#     scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))

#     def __repr__(self):
#             return f"<INTERPRETATIONSCENE id={self.id} {self.choice_id} {self.scene_id}>"


# class JobHeld(db.Model):
#     """Relationships between people and the film jobs they've held."""

#     __tablename__ = "jobs_held"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
#     film = db.relationship("Film", back_populates="jobs_held")
#     job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
#     job = db.relationship("Job", back_populates="jobs_held")
#     person_id = db.Column(db.Integer, db.ForeignKey("people.id"))
#     people = db.relationship("Person", back_populates="jobs_held")

#     def __repr__(self):
#         return f"<JOBHELD id={self.id} {self.job.title} {self.film.title}>"

#     def __str__(self):
#         return f"{self.job.title}, {self.film.title}"


# class PartPlayed(db.Model):
#     """Relationships between actors and the parts they've played."""

#     __tablename__ = "parts_played"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     person_id = db.Column(db.Integer, db.ForeignKey("people.id"))
#     person = db.relationship("Person", back_populates="parts_played")
#     character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))
#     character = db.relationship("Character")
#     film_id = db.Column(db.Integer, db.ForeignKey("films.id"))
#     film = db.relationship("Film")

#     def __repr__(self):
#         return f"<PARTPLAYED id={self.id} {self.person.lname} {self.character.name} {self.film.title}>"

#     def __str__(self):
#         return f"{self.person.fname} {self.person.lname}, {self.character.name}"

#     def age_during_film(self):
#         age = calculate_age_during_film(self.person, self.film)
#         return age
        


# class TopicCharacter(db.Model):
#     """Relationships between topics and characters."""

#     __tablename__ = "topic_characters"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
#     character_id = db.Column(db.Integer, db.ForeignKey("characters.id"))

#     def __repr__(self):
#             return f"<TOPICCHARACTER id={self.id} {self.topic_id} {self.character_id}>"


# class TopicScene(db.Model):
#     """Relationships between topics and scenes."""

#     __tablename__ = "topic_scenes"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
#     scene_id = db.Column(db.Integer, db.ForeignKey("scenes.id"))

#     def __repr__(self):
#             return f"<TOPICSCENE id={self.id} {self.scene_id} {self.topic_id}>"

# # -- END Relationship objects --


# def connect_to_db(flask_app, db_uri="postgresql:///motiveandcuedb", echo=True):
#     flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri #URI: Uniform Resource Identify-er
#     flask_app.config["SQLALCHEMY_ECHO"] = echo #Gives output for us to look at (that the computer is doing/has done)
#     flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #this is sometimes buggy when true

#     db.app = flask_app
#     db.init_app(flask_app)

#     print("Connected to the db!")


# if __name__ == "__main__":
#     from server import app
#     connect_to_db(app)

#     # os.system("dropdb motiveandcuedb")
#     # print("Table dropped.")
#     # os.system("createdb motiveandcuedb")
#     # print("Table created.")
    
#     db.create_all()